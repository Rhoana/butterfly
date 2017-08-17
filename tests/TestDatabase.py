import unittest as ut
import logging as log
import numpy.random as npr
import numpy as np
import datetime
import h5py
import bfly
import json
import sys
import os

def full_path(path):
    """ Prepend this file's directory to the path
    """
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, path)

def label_synapses(k_files, synapse_pairs, synapse_centers):
    """ make dummy dataset files

    Arguments
    ------------
        k_files: NamedStruct
            The constants for a synapse file
        synapse_pairs: np.ndarray
            All neuron pairs for all synapses
        synapse_centers: np.ndarray
            All vectors of synapse locations

    Returns
    ---------
        dict
            Ready to be written
    """
    # Get constant keywords
    k_neurons = k_files.SYNAPSE.NEURON_LIST
    k_center = k_files.SYNAPSE.POINT.NAME
    k_shape = k_files.SYNAPSE.POINT.LIST
    # Format neuron pairs and coordinates
    synapses = dict(zip(k_neurons, synapse_pairs.tolist()))
    synapses.update({
        k_center: dict(zip(k_shape, synapse_centers.tolist()))
    })
    return synapses

def make_neurons(neuron_n, info, seed):
    """ Make a number of neurons of a given data type

    Arguments
    ----------
    neuron_n: int
        The number of neurons to make
    info: np.iinfo
        Contains the dtype max and value
    seed: int
        The seed for predictable noise

    Returns
    --------
    np.ndarray:
        All the neurons
    """

    # Neuron ids
    npr.seed(seed)
    ids = npr.choice(info.max, neuron_n, True)
    return ids.astype(info.dtype)

def make_synapses(synapse_n, neuron_ids, info, seed):
    """ Make neuron pairs of a given data type

    Arguments
    ----------
    synapse_n: int
        The number of neuron pairs to make
    neuron_ids: np.ndarray
        All the neurosn to choose from
    info: np.iinfo
        Contains the dtype max and value
    seed: int
        The seed for predictable noise

    Returns
    --------
    np.ndarray:
        3xsynapse_n array of all pairs
    """

    pairs = np.zeros([2, synapse_n], dtype=info.dtype)
    # Both pairs
    for i in range(2):
        npr.seed(seed + i)
        pairs[i] = npr.choice(neuron_ids, synapse_n)
    return pairs

def make_centers(n_centers, zyx_shape, info, seed):
    """ Make many 3D vectors of a given data type

    Arguments
    ----------
    n_centers: int
        The number of centers to make
    zyx_shape: list
        The 3 dimensions of the volume
    info: np.iinfo
        Contains the dtype max and value
    seed: int
        The seed for predictable noise

    Returns
    --------
    np.ndarray:
        3xn_centers array of all vectors
    """

    zyx = np.zeros([3, n_centers], dtype=info.dtype)
    # All three dimensions
    for i in range(3):
        npr.seed(seed + i)
        zyx[i] = npr.choice(zyx_shape[i], n_centers)
    return zyx

class TestDatabase(ut.TestCase):
    """ set up tests for :class:`DatabaseLayer.Zodb`
    """
    DB_PATH = None
    DB_TYPE = 'Nodb'
    RUNTIME = bfly.UtilityLayer.RUNTIME()
    # Log to the command line
    log_info = {
        'stream': sys.stdout,
        'level': log.INFO
    }

    def test_database(self):
        """ test that :mod:`DatabaseLayer` can start \
and successfully deliver responses at a reasonable speed
        """
        # Log to command line
        log.basicConfig(**self.log_info)
        # Neuron and synapse counts
        neuron_n = 100
        synapse_n = 1000
        # Random seeds
        neuron_seed = 8675309
        synapse_seed = 525600
        # Set the channel and dataset paths
        channel = full_path('data/channel.h5')
        dataset = full_path('data')
        # shape, and type for temp file
        zyx_shape = [250, 2500, 2500]
        ids_info = np.iinfo(np.uint32)
        zyx_info = np.iinfo(np.uint32)

        # Make all the synapses and coordinates
        neuron_ids = make_neurons(neuron_n, ids_info, neuron_seed)
        synapse_pairs = make_synapses(synapse_n, neuron_ids, ids_info, synapse_seed)
        synapse_centers = make_centers(synapse_n, zyx_shape, zyx_info, synapse_seed)
        # Get constants for input files
        k_files = self.RUNTIME.DB.FILE
        k_synapse = k_files.SYNAPSE.DEFAULT
        # Make a data directory
        if not os.path.exists(dataset):
            os.makedirs(dataset)
        # Save synapse-connections.json
        synapse_dict = label_synapses(k_files, synapse_pairs, synapse_centers)
        with open(os.path.join(dataset, k_synapse), 'w') as sf:
            json.dump(synapse_dict, sf)

        # Make a dummy database
        db_class = getattr(bfly.DatabaseLayer, self.DB_TYPE)
        db = db_class(self.DB_PATH, self.RUNTIME)
        # Make a dummy config
        temp_config = {
            'experiments': [{
                'name': 'a',
                'samples': [{
                    'name': 'b',
                    'datasets': [{
                        'path': dataset,
                        'name': 'c',
                        'channels': [{
                            'path': channel,
                            'name': 'd'
                        }]
                    }]
                }]
            }]
        }

        # Load the configuraton json files
        db.load_config(temp_config)

        # Get constants for the database
        k_tables = self.RUNTIME.DB.TABLE
        s_table = k_tables.SYNAPSE.NAME
        ####
        # S1 : is_synapse
        ####
        # Should all be true
        for syn in range(synapse_n):
            res = db.is_synapse(s_table, channel, syn)
            # Raise exception if not true
            self.assertTrue(not not res)
        # Should all be false
        for syn in range(synapse_n, 2*synapse_n):
            res = db.is_synapse(s_table, channel, syn)
            # Raise exception if not false
            self.assertFalse(not not res)

if __name__ == '__main__':
    ut.main()
