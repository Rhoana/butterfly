from Database import Database
import numpy as np
import time

class Nodb(Database):
    """ Provides a :class:`Database` interface to ``dict``

    Arguments
    ----------
    path: str
        The file path to store and access the database
    RUNTIME: :class:`RUNTIME`
        Gets stored as :data:`RUNTIME`

    Attributes
    -----------
    RUNTIME: :class:`RUNTIME`
        With keywords needed to load files and use tables
    db: dict
        Keeps all from ``add_path`` in a simple key-value store \
and contains each table as a separate key
    log: :class:`MakeLog`.``logging``
        All formats for log messages
    """

    def __init__(self, path, _runtime):
        # Create or load the database
        Database.__init__(self, path, _runtime)
        # The database is a dictionary
        self.db = dict()

    def add_path(self,c_path,d_path):
        """ store a link from a ``c_path`` to a ``d_path``
        Overides :meth:`Database.add_path`

        Arguments
        ----------
        c_path: str
            The path to a given channel with images
        d_path: str
            The path to the dataset with metadata files
        """
        Database.add_path(self, c_path, d_path)
        # Map the c_path to the d_path
        self.db[c_path] = d_path

    def get_path(self, path):
        """ Map a channel path to a dataset path
        Overides :meth:`Database.get_path`

        Arguments
        ----------
        path: str
            The path to the given channel

        Returns
        --------
        str
            The dataset path for the  given ``path``
        """
        Database.get_path(self, path)
        # Get the correct path or input path by default
        return self.db.get(path, path)

    def get_all(self, table, path):
        """ Get all the entries in a table path
        Overides :meth:`Database.get_all`

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files

        Returns
        --------
        object or list
            A list of all entries in the table.
        """

        table_path = Database.get_all(self, table, path)
        # Get the list from the collection
        return self.db.get(table_path)

    def get_by_key(self, table, path, key):
        """ Get the entry for the key in the table.
        Overides :meth:`Database.get_by_key`

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
        dict
            The entry in the table for the given key.
        """

        table_path = Database.get_by_key(self, table, path, key)
        # Get the list from the collection
        collect = self.db.get(table_path)
        # Get information specific to the table
        table_field = self.RUNTIME.DB.TABLE[table]
        # Get primary key directly if possible
        if table_field.KEY.NAME in ['__id']:
            # If the collect doesn't have the key
            if len(collect) <= int(key):
                return []
            # Get entry from the collection
            return collect[int(key)]
        else:
            all_ids = collect[:,0]
            # Find potential spot for primary key
            first = np.searchsorted(all_ids, int(key))
            # Return if key value exists in array
            if all_ids[first] == int(key):
                return collect[first]
            return []

    def get_by_fun(self, table, path, fun):
        """ Get the entries where function is true.
        Overrides :meth:`Database.get_by_fun`

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
        list
        All entries where the function returns true
        """

        table_path = Database.get_by_fun(self, table, path, fun)
        # Get the actual collection
        collect = self.get_all(table, path)
        # Get the entry from the collection
        return [c for c in collect if fun(c)]

    ####
    # Override Database.add_entries
    ####
    def add_entries(self, table, path, t_keys, entries, update=1):
        """ Add an array or list of entries to a table
        Overrides :meth:`Database.add_entries`

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
        update: int
            1 to update old entries matching keys, and \
0 to write new entries ignoring old entries. Default 1.

        """
        # Get the name of the table
        table_path = Database.add_entries(self, table, path, t_keys, entries, update=1)

        # Time to add entries
        start = time.time()
        count = len(entries)
        self.log('ADD', count, table)

        # Get information specific to the table
        table_field = self.RUNTIME.DB.TABLE[table]
        # Add primary key if not explicit
        if table_field.KEY.NAME in ['__id']:
            # create full table
            keys = range(len(entries))
            entries = np.c_[keys, entries]
        # Sort by explicit primary key
        else:
            key_order = entries[:,0].argsort()
            entries = entries[key_order]

        # Add the entries to database
        self.db[table_path] = entries

        # Log diff and total time
        diff = time.time() - start
        self.log('ADDED', count, diff)
        return entries

    def synapse_ids(self, table, path, start, stop):
        """
        Overrides :meth:`Database.synapse_ids`
        """
        table_path = Database.synapse_ids(self, table, path, start, stop)
        # Get the array from the collection
        syns = self.db.get(table_path)
        # Get only the coordinates
        syns_zyx = syns[:,3:]
        # Get the indices within the bounds
        in_zyx = (syns_zyx >= start) & (syns_zyx < stop)
        result = syns[np.all(in_zyx, axis=1)]
        # Return all keys in the table
        listed = result[:,0].tolist()
        return listed

    def is_synapse(self, table, path, id_key):
        """
        Overrides :meth:`Database.is_synapse`
        """
        table_path = Database.is_synapse(self, table, path, id_key)
        # Get one value by key
        synapse = self.get_by_key(table, path, id_key)
        # Return boolean by length
        return not not len(synapse)

    def is_neuron(self, table, path, id_key):
        """
        Overrides :meth:`Database.is_neuron`
        """
        table_path = Database.is_neuron(self, table, path, id_key)
        # Get one value by key
        neuron = self.get_by_key(table, path, id_key)
        # Return boolean by length
        return not not len(neuron)

    def synapse_keypoint(self, table, path, id_key):
        """
        Overrides :meth:`Database.synapse_keypoint`
        """
        table_path = Database.synapse_keypoint(self, table, path, id_key)
        k_z, k_y, k_x = self.RUNTIME.DB.TABLE.ALL.POINT_LIST
        # Return a dictionary from a single result
        synapse = self.get_by_key(table, path, id_key)
        if not len(synapse):
            return {}
        return {
            k_z: synapse[-3],
            k_y: synapse[-2],
            k_x: synapse[-1]
        }

    def neuron_keypoint(self, table, path, id_key):
        """
        Overrides :meth:`Database.neuron_keypoint`
        """
        table_path = Database.neuron_keypoint(self, table, path, id_key)
        k_z, k_y, k_x = self.RUNTIME.DB.TABLE.ALL.POINT_LIST
        # Return a dictionary from a single result
        neuron = self.get_by_key(table, path, id_key)
        if not len(neuron):
            return {}
        return {
            k_z: neuron[-3],
            k_y: neuron[-2],
            k_x: neuron[-1]
        }

    def synapse_parent(self, table, path, id_key):
        """
        Overrides :meth:`Database.synapse_parent`
        """
        table_path = Database.synapse_parent(self, table, path, id_key)
        k_links = self.RUNTIME.FEATURES.LINKS
        # Return a dictionary from a single result
        synapse = self.get_by_key(table, path, id_key)
        if not len(synapse):
            return {}
        return {
            k_links.ID.NAME: synapse[0],
            k_links.PRE.NAME: synapse[1],
            k_links.POST.NAME: synapse[2]
        }

    def neuron_children(self, table, path, id_key, start, stop):
        """
        Overrides :meth:`Database.neuron_children`
        """
        table_path = Database.neuron_children(self, table, path, id_key, start, stop)
        # Get the array from the collection
        syns = self.db.get(table_path)

        # Get only the coordinates
        syns_zyx = syns[:, 3:]
        # Get the indices within the bounds
        in_zyx = (syns_zyx >= start) & (syns_zyx < stop)
        in_syns = syns[np.all(in_zyx, axis=1)]

        # Get only the lists of neurons
        neurons_1 = in_syns[:, 1]
        neurons_2 = in_syns[:, 2]
        # Get all synapse id values
        syns_ids = in_syns[:, 0]
        n_syns = len(syns_ids)

        # Get neurons matching the id key
        pre_neurons = syns_ids[neurons_1 == id_key]
        post_neurons = syns_ids[neurons_2 == id_key]
        # Synapses as keys in in a dictionary
        syn_dict = dict(zip(post_neurons, (2,)*n_syns))
        syn_dict.update(dict(zip(pre_neurons, (1,)*n_syns)))
        return syn_dict

    def all_neurons(self, table, path):
        """
        Overrides :meth:`Database.all_neurons`
        """
        table_path = Database.all_neurons(self, table, path)

        # Return all keys in the table
        result = self.get_all(table, path)
        listed = result[:,0].tolist()
        return listed
