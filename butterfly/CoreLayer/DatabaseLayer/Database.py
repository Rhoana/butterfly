import json, os
import numpy as np

class Database():

    def __init__(self, path, _runtime):
        # Get the database keywords
        self.RUNTIME = _runtime

    '''
    Interface for loading config
    '''
    def load_config(self, config):
        # Get file fields
        k_files = self.RUNTIME.DB.FILE
        # Get keywords for the BFLY_CONFIG
        k_list = k_files.CONFIG.GROUP_LIST
        k_path = k_files.CONFIG.PATH.NAME
        # Get the depth to the channels
        k_deep = len(k_list) - 1

        # Join lists from config groups
        def cat_lists(groups, level):
            # Get the next group key
            lev_key = k_list[level]
            # Get a list of lists of all the next groups
            g_lists = [g.get(lev_key, []) for g in groups]
            # Get list of all groups from groups
            return [g for l in g_lists for g in l]

        # Join all lists from within config
        all_lists = reduce(cat_lists, range(k_deep), [config])

        # Map channel paths to datasource paths
        def map_paths(all_map, src):
            # Get the channel key and list
            c_key = k_list[k_deep]
            c_list = src.get(c_key,{})
            # Get the source path
            path = src.get(k_path)
            # Add none to map if no path
            if not path: return all_map
            # Map new channel paths to path if exists
            a_map = {c[k_path]: path for c in c_list}
            return dict(all_map, **a_map)

        # Create dictionary from each channel in lists
        all_paths = reduce(map_paths, all_lists, {})

        # Add all paths to the database
        return self.add_paths(all_paths)


    '''
    Interface for adding paths
    '''

    def add_paths(self, all_paths):
        # Get unique dataset paths
        dataset_paths = set(all_paths.values())
        # Add all paths to database
        for c_path,d_path in all_paths.iteritems():
            self.add_one_path(c_path, d_path)
        # Add all tables for each path
        for d_path in dataset_paths:
            self.add_tables(d_path)
            synapses = self.load_synapses(d_path)
            self.load_neurons(d_path, synapses)
        # Save to disk
        self.commit()
        return self

    # Must be overwritten
    def add_one_path(self, c_path, d_path):
        return ''

    '''
    Interface for adding tables
    '''

    def add_tables(self, path):
        # Get keywords for the database
        k_list = self.RUNTIME.DB.TABLE.LIST
        # Create all tables for the path
        for k_table in k_list:
            # Make a table from path and table name
            self.add_one_table(k_table, path)
        return ''

    # Must be overwritten
    def add_one_table(self, table, path):
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, path)

    '''
    Interface for loading entries
    '''
    def load_synapses(self, path):
        # Get file fields
        k_files = self.RUNTIME.DB.FILE
        # Get keywords for input file
        k_file = k_files.SYNAPSE.NAME
        k_point = k_files.SYNAPSE.POINT.NAME
        k_points_in = k_files.SYNAPSE.POINT.LIST
        k_nodes_in = k_files.SYNAPSE.NEURON_LIST
        # Get the full path to the synapse file
        full_path = os.path.join(path, k_file)

        try:
            # Begin adding synapses to database
            with open(full_path, 'r') as f:
                all_dict = json.load(f)
                point_dict = all_dict[k_point]
        # Return if not valid file or json
        except (IOError, ValueError):
            return []

        # Transpose the list of all synapses
        links = map(all_dict.get, k_nodes_in)
        center = map(point_dict.get, k_points_in)
        synapses = np.uint32(links + center).T

        # Add synapses to database
        self.add_synapses(path, synapses)
        return synapses

    def load_neurons(self, path, synapses):
        # Get all source and target nodes
        all_tgt = np.unique(synapses[:,1])
        all_src, arg_src = np.unique(synapses[:,0], True)
        src_dict = dict(zip(all_src, arg_src))
        # Find neurons that are never targets
        only_src = list(set(all_src) - set(all_tgt))
        src_keys = map(src_dict.get, only_src)
        # Get all neuron lists from synapse targets, sources
        neuron_src = np.delete(synapses[src_keys], 1, 1)
        neuron_tgt = np.delete(synapses, 0, 1)
        # Get full neuron list from source and target
        neurons = np.r_[neuron_src, neuron_tgt]

        # Add neuons to database
        self.add_neurons(path, neurons)
        return neurons

    '''
    Interface for adding entries
    '''
    def add_synapses(self, path, synapses):
        # Get database fields
        k_tables = self.RUNTIME.DB.TABLE
        # Get keywords for the database
        k_synapse = k_tables.SYNAPSE.NAME
        # List all the syapse database keys
        k_nodes_out = k_tables.SYNAPSE.NEURON_LIST
        k_points_out = k_tables.ALL.POINT_LIST
        k_keys = k_nodes_out + k_points_out

        # Add entries
        return self.add_entries(k_synapse, path, k_keys, synapses)

    def add_neurons(self, path, neurons):
        # Get database fields
        k_tables = self.RUNTIME.DB.TABLE
        # Get keywords for the database
        k_neuron = k_tables.NEURON.NAME
        # List all the syapse database keys
        k_node_out = k_tables.NEURON.KEY.NAME
        k_points_out = k_tables.ALL.POINT_LIST
        k_keys = [k_node_out] + k_points_out

        # Add entries
        return self.add_entries(k_neuron, path, k_keys, neurons)

    def add_entries(self, table, path, t_keys, entries):
        # Typecast values uniformly
        def cast(value):
            # convert if numpy datatype
            if isinstance(value, np.number):
                return value.item()
            return value
        # Add entries to database
        def add_entry(entry):
            # Add a tuple entry as a dict
            if hasattr(entry, '__len__'):
                d_entry = dict(zip(t_keys, map(cast,entry)))
                self.add_entry(table, path, d_entry)
                return d_entry
        # add all the entries
        dict_entries = map(add_entry, entries)
        # Save to disk
        self.commit()
        return dict_entries

    # Must be overwritten
    def add_entry(self, table, path, entry):
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, path)

    '''
    Interface for getting
    '''

    # Must be overwritten
    def get_path(self, path):
        return path

    # Must be overwritten
    def get_table(self, table, path):
        real_path = self.get_path(path)
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, real_path)

    def get_entry(self, table, path, key=None, **keywords):
        # Get the necessary keywords
        k_tables = self.RUNTIME.DB.TABLE
        # Use key if no keywords
        if not len(keywords):
            # Return all if no key
            if key is None:
                return self.get_all(table, path)
            # Filter by filter fun if callable
            if callable(key):
                result = self.get_by_fun(table, path, key)
                return result if result else []
            # Filter by a secondary key
            if table == k_tables.NEURON.NAME:
                keywords[k_tables.NEURON.KEY.NAME] = key
            # Treat the key as the primary key
            else:
                return self.get_by_key(table, path, key)
        # Filter the database by keywords
        result = self.get_by_keywords(table, path, **keywords)
        return result if result else []

    # Must be overwritten
    def get_all(self, table, path):
        return self.get_table(table, path)

    # Must be overwritten
    def get_by_key(self, table, path, key):
        return  self.get_table(table, path)

    # Must be overwritten
    def get_by_fun(self, table, path, fun):
        return  self.get_table(table, path)

    def get_by_keywords(self, table, path, **keys):
        values = lambda e: map(e.get, keys.keys())
        getter = lambda e: values(e) == keys.values()
        return self.get_by_fun(table, path, getter)

    '''
    Interface for saving to disk
    '''
    # Must be overwritten
    def commit(self):
        return ''

