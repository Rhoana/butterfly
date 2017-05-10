import time
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
    log: :class:`MakeLog`.``logging``
        All formats for log messages
    RUNTIME: :class:`RUNTIME`
        With keywords needed to load files and use tables
    """
    def __init__(self, path, _runtime):
        # Get the database keywords
        self.RUNTIME = _runtime
        # Create info logger
        log_list = _runtime.ERROR.DB
        self.log = _runtime.MAKELOG(log_list).logging

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
        k_range = range(len(k_list) - 1)

        # Join lists from config groups
        def cat_lists(groups, level):
            # Get the next group key
            lev_key = k_list[level]
            # Get a list of lists of all the next groups
            g_lists = [g.get(lev_key, []) for g in groups]
            # Get list of all groups from groups
            return [g for l in g_lists for g in l]

        # Join all lists from within config
        all_lists = reduce(cat_lists, k_range, [config])
        # Load all files for each dataset
        map(self.load_all, all_lists)

        # Save to disk
        self.commit()
        return self

    def load_all(self, source):
        """ Load the tables, synapses, and neuron configs
        Arguments
        ----------
        source: dict
            The configuration options for a dataset
        """
        # Get file fields
        k_files = self.RUNTIME.DB.FILE
        # Get keywords for the BFLY_CONFIG
        k_list = k_files.CONFIG.GROUP_LIST
        k_path = k_files.CONFIG.PATH.NAME
        # Get the key to the channels
        k_channel = k_list[-1]

        # Set custom names of files
        for nf in map(k_files.get, k_files.DB_LIST):
            nf.VALUE = source.get(nf.NAME, nf.DEFAULT)

        # list of channels for the dataset path
        c_list = source.get(k_channel, [])
        d_path = source.get(k_path, '')

        # Add all channel paths to database
        for c_dict in c_list:
            c_path = c_dict.get(k_path, '')
            self.add_path(c_path, d_path)

        # if a real dataset and channel paths
        if d_path and len(c_list):
            # Add all tables for the dataset path
            self.add_tables(d_path)
            # Load all synapses and neurons
            synapses = self.load_synapses(d_path)
            self.load_neurons(d_path, synapses)

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
        k_file = k_files.SYNAPSE.VALUE
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
        # return if not synapses
        if not len(synapses):
            return synapses
        ####
        # Get neurons from loaded synapses
        ####

        # All unqiue source nodes and their keys
        all_src, src_keys = np.unique(synapses.T[0], True)
        # All unique target nodes and their keys
        all_tgt, tgt_keys = np.unique(synapses.T[1], True)
        # Find keys for neurons that are never targets
        only_src = list(set(all_src) - set(all_tgt))
        src_dict = dict(zip(all_src, src_keys))
        src_keys = map(src_dict.get, only_src)
        # Get all neuron lists from synapse targets, sources
        neuron_tgt = np.delete(synapses[tgt_keys], 0, 1)
        neuron_src = np.delete(synapses[src_keys], 1, 1)
        # Get full neuron list from source and target
        neurons = np.r_[neuron_src, neuron_tgt]

        # Add neurons to database
        self.add_neurons(path, neurons)
        return neurons

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
with dictionary keys taken from ``SYNAPSE.FULL_LIST`` \
field of :data:`RUNTIME.DB`

        """
        # Get database fields
        k_tables = self.RUNTIME.DB.TABLE
        # Get keywords for the database
        k_synapse = k_tables.SYNAPSE.NAME
        # List all the syapse database keys
        k_keys = k_tables.SYNAPSE.FULL_LIST

        # Add entries
        return self.add_entries(k_synapse, path, k_keys, synapses, 0)

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
with dictionary keys from the ``NEURON.FULL_LIST`` \
field of :data:`RUNTIME.DB`

        """

        # Get database fields
        k_tables = self.RUNTIME.DB.TABLE
        # Get keywords for the database
        k_neuron = k_tables.NEURON.NAME
        # List all the syapse database keys
        k_keys = k_tables.NEURON.FULL_LIST

        # Add entries
        return self.add_entries(k_neuron, path, k_keys, neurons, 0)

    def add_entries(self, table, path, t_keys, entries, update=1):
        """ Add an array or list of entries to a table
        Must be overridden by derived class.
        """
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, path)

    def add_entry(self, table, path, entry, update=1):
        """ and a single entry to a table for a path
        Overides :meth:`Database.add_entry`

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        entry: dict
            The mapping of keys to values for the entry
        update: int
            1 to update old entries matching keys, and \
0 to write new entries ignoring old entries. Default 1.

        Returns
        --------
        dict
            The value of the entry
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

    def synapse_ids(self, table, path, start, stop):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def is_synapse(self, table, path, id_key):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def is_neuron(self, table, path, id_key):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def synapse_keypoint(self, table, path, id_key):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def neuron_keypoint(self, table, path, id_key):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def synapse_parent(self, table, path, id_key):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def neuron_children(self, table, path, id_key):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def all_neurons(self, table, path):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

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

