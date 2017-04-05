import json, os
import numpy as np

class Database():
    """ Stores tables to respond to :meth:`API._feature_info`

    Arguments
    ----------
    path: str
        The file path to store and access the database
    _runtime: :class:`RUNTIME`
        Gets stored as :data:`RUNTIME`

    Attributes
    -----------
    RUNTIME: :class:`RUNTIME`
        With keywords needed to load files and use tables
    """
    def __init__(self, path, _runtime):
        # Get the database keywords
        self.RUNTIME = _runtime

    def load_config(self, config):
        """ Loads all files from ``config`` into database

        Arguments
        ----------
        config: dict
            all data from :mod:`UtilityLayer.rh_config`

        Returns
        ---------
        :class:`Database`
            the derived database class instance
        """
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

    def add_paths(self, all_paths):
        """
        Arguments
        ----------
        all_paths: dict
            The mapping from channel path to dataset path

        Returns
        ---------
        :class:`Database`
            the derived database class instance
        """
        # Get unique dataset paths
        dataset_paths = set(all_paths.values())
        # Add all paths to database
        for c_path,d_path in all_paths.iteritems():
            self.add_path(c_path, d_path)
        # Add all tables for each path
        for d_path in dataset_paths:
            self.add_tables(d_path)
            # Load all the blocks
            self.load_blocks(d_path)
            # Load all synapses and neurons
            synapses = self.load_synapses(d_path)
            self.load_neurons(d_path, synapses)
        # Save to disk
        self.commit()
        return self

    def add_path(self, c_path, d_path):
        """ store a link from a ``c_path`` to a ``d_path``
        Must be overridden by derived class.

        Arguments
        ----------
        c_path: str
            The path to a given channel with images
        d_path: str
            The path to the dataset with metadata files
        """
        pass

    def add_tables(self, path):
        """ Store all the tables for a given path

        Arguments
        ----------
        path: str
            The dataset path to metadata files
        """
        # Get keywords for the database
        k_list = self.RUNTIME.DB.TABLE.LIST
        # Create all tables for the path
        for k_table in k_list:
            # Make a table from path and table name
            self.add_table(k_table, path)
        return self

    def add_table(self, table, path):
        """ Add a table to the database
        Must be overridden by derived classes

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files

        Returns
        --------
        str or bool
            The table name combining ``table`` and ``path`` \
The derived classes should return whether the table was \
added successfully.
        """
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, path)

    def load_synapses(self, path):
        """ Load all the synapse information from files

        Arguments
        ----------
        path: str
            The dataset path to metadata files

        Returns
        --------
        numpy.ndarray
            The Nx5 array of pre, post, z, y, x values \
where N is the number of synapses for the ``path``.
        """
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
            # Load the file with the synapses
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
        """ Load all the neuron information from files

        Arguments
        ----------
        path: str
            The dataset path to metadata files
        synapses: numpy.ndarray
            The Nx5 array of pre, post, z, y, x values \
where N is the number of synapses for the ``path``.

        Returns
        --------
        numpy.ndarray
            The Nx4 array of id, z, y, x values \
where N is the number of neurons for the ``path``.
        """
        ####
        # Get neurons from loaded synapses
        ####

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

        # Add neurons to database
        self.add_neurons(path, neurons)
        return neurons

    def load_blocks(self, path):
        """ Load all the block information from files

        Arguments
        ----------
        path: str
            The dataset path to metadata files

        Returns
        --------
        numpy.ndarray
            The Nx6 array of z0, y0, x0, z1, y1, x1 values \
where N is the number of blocks for the ``path``.
        """
        # Get file fields
        k_files = self.RUNTIME.DB.FILE
        # Get name of the block file
        k_file = k_files.BLOCK.NAME
        # Get boundary keys for the block file
        k_bounds = k_files.BLOCK.BOUND.NAME
        k_start = k_files.BLOCK.BOUND.START
        k_shape = k_files.BLOCK.BOUND.SHAPE
        # Get neuron keys for the block file
        k_blocks = k_files.BLOCK.BLOCK.NAME
        # Get the full path to the block file
        full_path = os.path.join(path, k_file)

        try:
            # Load the file with all blocks
            with open(full_path, 'r') as f:
                all_dict = json.load(f)
                all_blocks = all_dict[k_blocks]
        # Return if not valid file or json
        except (IOError, ValueError):
            return []

        # Reformat each of the blocks as needed
        def reformat_block(block):
            # Get the bounds for the volume
            bound_start = map(block[0].get, k_start)
            bound_shape = map(block[0].get, k_shape)
            bound_end = list(np.uint32(bound_start) + bound_shape)
            # Get the actual neuron ids
            def get_full_id(id_map):
                return id_map[1]
            bound_ids = map(get_full_id, block[1])
            # Return the bounds and neurons
            return [bound_start, bound_end, bound_ids]

        # Get the list of lists for each block
        block_list = map(reformat_block, all_blocks)
        # Add the blocks to the database
        return self.add_blocks(path, block_list)

    def add_blocks(self, path, blocks):
        """ Add all the blocks to the database

        Arguments
        ----------
        path: str
            The dataset path to metadata files
        blocks: list of lists
            The N lists of three lists with start bounds, end bounds, \
and neurons where N is the number of blocks for the ``path``.

        Returns
        --------
        list
            A list of dicts from each row of ``blocks`` \
with dictionary keys taken from both ``BLOCK.KEY_LIST``

        """
        # Get database fields
        k_tables = self.RUNTIME.DB.TABLE
        # Get table key_values
        k_keys = k_tables.BLOCK.KEY_LIST
        k_block = k_tables.BLOCK.NAME

        # Add entries
        return self.add_entries(k_block, path, k_keys, blocks)

    def add_synapses(self, path, synapses):
        """ Add all the synapases to the database

        Arguments
        ----------
        path: str
            The dataset path to metadata files
        synapses: numpy.ndarray
            The Nx5 array of pre, post, z, y, x values \
where N is the number of synapses for the ``path``.

        Returns
        --------
        list
            A list of dicts from each row of ``synapses`` \
with dictionary keys taken from both ``SYNAPSE.NEURON_LIST`` \
and ``ALL.POINT_LIST`` fields of :data:`RUNTIME.DB`

        """
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
        """ Add all the neurons to the database

        Arguments
        ----------
        path: str
            The dataset path to metadata files
        neurons: numpy.ndarray
            The Nx4 array of id, z, y, x values \
where N is the number of neurons for the ``path``.

        Returns
        --------
        list
            A list of dicts from each row of ``neurons`` \
with dictionary keys taken from both ``NEURON.KEY.NAME`` \
and ``ALL.POINT_LIST`` fields of :data:`RUNTIME.DB`

        """

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
        """ Add an numpy.array of entries to a table

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        t_keys: list
            All of ``K`` keys for each row of ``entries``
        entries: numpy.ndarray or list
            ``N`` by ``K`` array or list where ``N`` is the number \
of entries to add and ``K`` is the number of keys per entry

        """
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

    def add_entry(self, table, path, entry):
        """ and a single entry to a table for a path
        Must be overridden by derived class.

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        entry: dict
            The mapping of keys to values for the entry

        Returns
        --------
        str or bool
            Full database name of the table for a path. \
The derived classes should return whether the entry was \
added successfully.
        """
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, path)

    def get_path(self, path):
        """ Map a channel path to a dataset path
        Must be overridden by derived class.

        Arguments
        ----------
        path: str
            The path to the given channel

        Returns
        --------
        str
            The dataset path for the  given ``path``
        """
        pass

    def get_table(self, table, path):
        """ Get the actual table for a given path
        Must be overridden by derived class.

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files

        Returns
        --------
        str or object
            Full database name of the table for a path. \
The derived classes should actually return the python \
object reference to the real table.
        """
        real_path = self.get_path(path)
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, real_path)

    def get_entry(self, table, path, key=None, **keywords):
        """ Get an actual entry in the database

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        key: int or callable
            Either the primary key value for any entry \
or a filter function to get multiple entries
        keywords: dict
            The entry field values to filter entries

        Returns
        --------
        dict or list
            A single entry given as a dict or multiple \
entries given as a list of dict entries.
        """

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

    def get_all(self, table, path):
        """ Get all the entries in a table path
        Must be overridden by derived class.

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files

        Returns
        --------
        object or list
            The object reference from :meth:`get_table`. \
The derived class should list all entries in the table.
        """

        return self.get_table(table, path)

    def get_by_key(self, table, path, key):
        """ Get the entry for the key in the table.
        Must be overridden by derived class.

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        key: int
            The primary key value for any entry

        Returns
        --------
        object or dict
            The object reference from :meth:`get_table`. \
The derived class should give an entry in the table.
        """
        return  self.get_table(table, path)

    def get_by_fun(self, table, path, fun):
        """ Get the entries where function is true.
        Must be overridden by derived class.

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        fun: int
            The function to filter the table entries

        Returns
        --------
        object or list
            The object reference from :meth:`get_table`. \
The derived class should list all entries that make the \
function return a true value.
        """
        return  self.get_table(table, path)

    def get_by_keywords(self, table, path, **keys):
        """ Get the entries where the fields match ``keys``.
        Must be overridden by derived class.

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        keys: dict
            The keywords to filter the table entries

        Returns
        --------
        object or list
            The object reference from :meth:`get_table`. \
The derived class should list all entries that match the \
keyword value paris given in ``keys``.
        """
        # Make keyword filter
        def key_filter(v):
            values = map(v.get, keys.keys())
            # Compare all values with keywords
            compare = zip(values, keys.values())
            return all(a==b for a,b in compare)
        # Filter table by keywords
        return self.get_by_fun(table, path, key_filter)

    def commit(self):
        """ Save all database changes to the database file.
        Must be overridden by derived class.
        """
        pass

