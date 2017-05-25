from Database import Database
from pymongo import MongoClient
from pymongo import ASCENDING
import numpy as np
import rtree
import time
import os

class Mongodb(Database):
    """ Provides a :class:`Database` interface to ``pymongo``

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
    synapse_rtree: rtree.index.Index
        Keeps all synapse positions for spatial indexing
    mongo_db: pymongo.database
        Keeps all full collections of neurons and synapses
    log: :class:`MakeLog`.``logging``
        All formats for log messages
    """

    def __init__(self, path, _runtime):
        # Create or load the database
        Database.__init__(self, path, _runtime)
        # Get the port for the mongo server
        mongo_port = _runtime.DB.PORT.VALUE
        # Format path as folder, not file
        rtree_prefix = path.replace('.','_')

        # Make a 3d spatial index
        zyx = rtree.index.Property()
        zyx.dimension = 3

        # Delete all rtree files
        for ext in ['.idx','.dat']:
            x_file = rtree_prefix + ext
            if os.path.exists(x_file):
                os.remove(x_file)

        # The synapse positions are stored in an rtree
        self.synapse_rtree = rtree.index.Index(rtree_prefix, properties = zyx)

        ########
        # Connect to the mongo client
        mongo_client = MongoClient('localhost', mongo_port)
        # Create or open the root database
        self.mongo_db = mongo_client['root']
        # Simple dictionary for paths
        self.path_db = dict()

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
        self.path_db[c_path] = d_path

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
        return self.path_db.get(path, path)

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
        collect = self.mongo_db[table_path]
        # Get information specific to the table
        table_field = self.RUNTIME.DB.TABLE[table]
        key_name = table_field.KEY.NAME
        # Find one value by the key name
        found = collect.find_one({key_name: key})
        return found if found else {}

    ####
    # Override Database.add_entries
    ####
    def add_entries(self, table, path, t_keys, entries):
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
        """
        # Get the name of the table
        table_path = Database.add_entries(self, table, path, t_keys, entries)

        # Time to add entries
        start = time.time()
        count = len(entries)
        self.log('ADD', count, table)

        # Get information specific to the table
        table_field = self.RUNTIME.DB.TABLE[table]
        key_name = table_field.KEY.NAME

        # Add primary key if not explicit
        if key_name in ['__id']:
            # create full table
            indexes = range(len(entries))
            entries = np.c_[indexes, entries]
        # Sort by explicit primary key
        else:
            key_order = entries[:,0].argsort()
            entries = entries[key_order]

        # Make the dictionaries from the keys
        def diction(v):
            return dict(zip(t_keys, v.tolist()))
        dict_entries = [diction(v) for v in entries]

        ##########
        # Add the entries to database
        collect = self.mongo_db[table_path]
        # Set to update if updating or empty database
        updating = self.RUNTIME.DB.UPDATE.VALUE
        if updating or not collect.count():
            # Clear the collection
            collect.remove()
            # Create the synapse index
            id_index = [(key_name, ASCENDING)]
            collect.create_index(id_index, unique=True)
            # Add all the dictionaries to the collection
            collect.insert_many(dict_entries)
        self.log('ALL','Adding to RTree...')
        ##########
        # Add the synapses to the rtree
        k_tables = self.RUNTIME.DB.TABLE
        if table == k_tables.SYNAPSE.NAME:
            # Get the coordinates for the rtree
            coords = k_tables.ALL.POINT_LIST
            for d in dict_entries:
                # Insert into the rtree
                i = d[key_name]
                zyx = [d[c] for c in coords]*2
                self.synapse_rtree.insert(i, zyx)

        # Log diff and total time
        diff = time.time() - start
        self.log('ADDED', count, diff)
        return dict_entries

    def synapse_ids(self, table, path, start, stop):
        """
        Overrides :meth:`Database.synapse_ids`
        """
        table_path = Database.synapse_ids(self, table, path, start, stop)
        # Convert from [[z0,y0,x0], [z1,y1,x1]]
        # to [z0, y0, x0, z1, y1, x1]
        rect = np.uint32([start, stop]).flatten()
        # Get all ids in the bounds
        within = self.synapse_rtree.intersection(rect)
        return list(within)

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
            k_z: synapse[k_z],
            k_y: synapse[k_y],
            k_x: synapse[k_x]
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
            k_z: neuron[k_z],
            k_y: neuron[k_y],
            k_x: neuron[k_x]
        }

    def synapse_parent(self, table, path, id_key):
        """
        Overrides :meth:`Database.synapse_parent`
        """
        table_path = Database.synapse_parent(self, table, path, id_key)
        k_links = self.RUNTIME.FEATURES.LINKS
        # Get pre and post-synaptic names
        k_synapse = self.RUNTIME.DB.TABLE.SYNAPSE
        n1, n2 = k_synapse.NEURON_LIST
        key_name = k_synapse.KEY.NAME
        # Return a dictionary from a single result
        synapse = self.get_by_key(table, path, id_key)
        if not len(synapse):
            return {}
        return {
            k_links.ID.NAME: synapse[key_name],
            k_links.PRE.NAME: synapse[n1],
            k_links.POST.NAME: synapse[n2]
        }

    def neuron_children(self, table, path, id_key, start, stop):
        """
        Overrides :meth:`Database.neuron_children`
        """
        table_path = Database.neuron_children(self, table, path, id_key, start, stop)

        # Get the indices within the bounds
        in_syns = self.synapse_ids(table, path, start, stop)

        # Get the array from the collection
        collect = self.mongo_db[table_path]
        # Get pre and post-synaptic names
        k_synapse = self.RUNTIME.DB.TABLE.SYNAPSE
        n1, n2 = k_synapse.NEURON_LIST
        key_name = k_synapse.KEY.NAME
        # Get pre and post synapses
        pre_syns = []
        post_syns = []
        # Add all bounded pre synapses
        for pre in collect.find({n1:id_key}):
            if pre in in_syns:
                pre_syns.append(pre)
        # Add all bounded post synapses
        for post in collect.find({n2:id_key}):
            if post in in_syns:
                post_syns.append(post)

        # Synapses as keys in in a dictionary
        syn_dict = dict(zip(post_syns, (2,)*len(post_syns)))
        syn_dict.update(dict(zip(pre_syns, (1,)*len(pre_syns))))
        return syn_dict

    def all_neurons(self, table, path):
        """
        Overrides :meth:`Database.all_neurons`
        """
        table_path = Database.all_neurons(self, table, path)

        # Get information specific to the neuron table
        neuron_field = self.RUNTIME.DB.TABLE.NEURON
        key_name = neuron_field.KEY.NAME
        # Return all keys in the table
        collect = self.mongo_db[table_path]
        listed = collect.distinct(key_name)
        return listed
