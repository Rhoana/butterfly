import os
import csv
import time
import json
import numpy as np
import logging as log

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
        k_dpath = k_files.CONFIG.DPATH.NAME
        k_path = k_files.CONFIG.PATH.NAME
        # Get the key to the channels
        k_channel = k_list[-1]

        # Set custom names of files
        for nf in map(k_files.get, k_files.DB_LIST):
            nf.VALUE = source.get(nf.NAME, nf.DEFAULT)

        # list of channels for the dataset path
        c_list = source.get(k_channel, [])
        d_path = source.get(k_path, '')

        # List used paths
        done_paths = ['']

        # Add all channel paths to database
        for c_dict in c_list:
            # Get paths to map to data
            c_path = c_dict.get(k_path, '')
            c_dpath = c_dict.get(k_dpath, d_path)
            if c_dpath:
                # Map the path to the data path
                self.add_path(c_path, c_dpath)
            # if we found a new data path
            if c_dpath not in done_paths:
                # Add all tables for the dataset path
                self.add_tables(c_dpath)
                # Load all synapses and neurons
                synapses = self.load_synapses(c_dpath)
                self.load_neurons(c_dpath, synapses)
                # Mark the dataset path as fully loaded
                done_paths.append(c_dpath)

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

        # Get file fields
        k_files = self.RUNTIME.DB.FILE
        # Get keywords for input file
        k_file = k_files.SOMA.VALUE
        k_file = os.path.join(path, k_file)

        if os.path.exists(k_file):
            msg = "Loading neuron centers from {}"
            log.info(msg.format(k_file))
            # Load the csv
            with open(k_file, 'r') as jf:
                # Keep a list of synapseless soma
                new_neurons = []
                # Add each new center point to database
                for soma in json.load(jf):
                    # Make a numpy uint32 coorinate array
                    k_soma = ['neuron_id', 'z', 'y', 'x']
                    new_soma = np.uint32(map(soma.get, k_soma))
                    soma_id = new_soma[0]
                    # Find the correct ID
                    neuron_ids = neurons.T[0]
                    # If the soma has a synapse
                    if soma_id in neuron_ids:
                        # Insert into the correct ID
                        soma_index = np.argwhere(neuron_ids == soma_id)[0][0]
                        neurons[soma_index] = new_soma
                    else:
                        # Add new synapseless neuron
                        new_neurons.append(new_soma)

                # Add new neurons to full neurons list
                if len(new_neurons):
                    neurons = np.r_[neurons, new_neurons]

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
        return self.add_entries(k_neuron, path, k_keys, neurons)

    def add_entries(self, table, path, t_keys, entries):
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

    def synapse_keypoint(self, table, path, id_key, scales):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def neuron_keypoint(self, table, path, id_key, scales):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def synapse_parent(self, table, path, id_key):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def neuron_children(self, table, path, id_key, start, stop):
        """
        Must be overridden by derived class.
        """
        return self.get_table(table, path)

    def all_neurons(self, table, path):
        """
        Must be overridden by derived class.
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

    def commit(self):
        """ Save all database changes to the database file.
        Must be overridden by derived class.
        """
        pass

