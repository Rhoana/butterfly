from numpy.random import randint
from numpy.random import random
from numpy.random import choice
import unittest as ut
import logging as log
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

class TestDatabase(ut.TestCase):
    """ set up tests for :class:`DatabaseLayer.Zodb`
    """
    DB_PATH = None
    DB_TYPE = 'Nodb'
    # Neuron max and count
    n_count = 100
    # Synapse count
    s_count = 1000
    # shape, and type for temp file
    h_shape = [1, 25000, 25000]
    h_type = 32
    RUNTIME = bfly.UtilityLayer.RUNTIME()
    # Set the channel and dataset paths
    channel = full_path('data/channel.h5')
    dataset = full_path('data')
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

        # Make a data directory
        if not os.path.exists(self.dataset):
            os.makedirs(self.dataset)
        # Save dummy h5 files and config files
        # self.make_h5()
        self.make_dataset()

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
                        'path': self.dataset,
                        'name': 'c',
                        'channels': [{
                            'path': self.channel,
                            'name': 'd'
                        }]
                    }]
                }]
            }]
        }

        # Load the configuraton json files
        db.load_config(temp_config)
        self.db = db

        # Get basic database keywords
        k_tables = self.RUNTIME.DB.TABLE
        s_table = k_tables.SYNAPSE.NAME
        ####
        # S1 : is_synapse
        ####
        # Should all be true
        for syn in range(self.s_count):
            res = self.db.is_synapse(s_table, self.channel, syn)
            # Raise exception if not true
            self.assertTrue(not not res)
        # Should all be false
        for syn in range(self.s_count, 2*self.s_count):
            res = self.db.is_synapse(s_table, self.channel, syn)
            # Raise exception if not false
            self.assertFalse(not not res)

    def make_h5(self):
        """ make a dummy h5 file for testing
        """
        # Get the datatype, noise range, and size
        dtype = getattr(np, 'uint{}'.format(self.h_type))
        dmax = 2 ** self.h_type
        dsize = self.h_shape
        # Create the file from a path
        with h5py.File(self.channel, 'w') as fd:
            # Make a random array
            pattern = randint(dmax, size= dsize, dtype= dtype)
            fd.create_dataset('stack', data= pattern)
        # Log that the file path was written
        msg = """
||| Testing TestDatabase |||
The h5 file {} is written.
""".format(self.channel)
        log.info(msg)

    def make_dataset(self):
        """ make dummy dataset files for database
        """
        # Get constants
        k_files = self.RUNTIME.DB.FILE
        # Get max data value
        dmax = 2 ** self.h_type
        # Generate neuron list
        self.neurons = choice(dmax, self.n_count)

        ####
        # Make synapses
        ####
        k_neurons = k_files.SYNAPSE.NEURON_LIST
        k_center = k_files.SYNAPSE.POINT.NAME
        k_shape = k_files.SYNAPSE.POINT.LIST
        # Take random pairs
        gen = self.neurons, 2
        syn = range(self.s_count)
        cells = [choice(*gen) for _ in syn]
        cells = np.uint32(cells).T.tolist()
        # Put pairs at random coordinates
        shapes = [self.s_count, 3]
        coords = random(shapes)*self.h_shape
        coords = np.uint32(coords).T.tolist()
        # Format neuron pairs and coordinates
        synapses = dict(zip(k_neurons, cells))
        synapses.update({
            k_center: dict(zip(k_shape, coords))
        })

        ####
        # Write synapses to file
        ####
        k_synapse = k_files.SYNAPSE.DEFAULT
        synapsefile = os.path.join(self.dataset, k_synapse)
        with open(synapsefile, 'w') as sf:
            json.dump(synapses, sf)

if __name__ == '__main__':
    ut.main()
