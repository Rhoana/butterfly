from numpy.random import randint
from numpy.random import random
from numpy.random import choice
import unittest as ut
import numpy as np
import datetime
import logging
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
    DB_TYPE = 'Zodb'
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
        'level': logging.INFO
    }

    @classmethod
    def test_database(cls):
        """ test that :mod:`DatabaseLayer` can start \
and successfully deliver responses at a reasonable speed
        """

        # Log to command line
        logging.basicConfig(**cls.log_info)
        # Make a custom log for this test
        cls._log = cls.make_log()

        # Make a data directory
        if not os.path.exists(cls.dataset):
            os.makedirs(cls.dataset)
        # Save dummy h5 files and config files
        cls.make_h5()
        cls.make_dataset()

        # Make a dummy database
        db_class = getattr(bfly.DatabaseLayer, cls.DB_TYPE)
        db = db_class(cls.DB_PATH, cls.RUNTIME)
        # Make a dummy config
        temp_config = {
            'bfly': {
                'experiments': [{
                    'name': 'a',
                    'samples': [{
                        'name': 'b',
                        'datasets': [{
                            'path': cls.dataset,
                            'name': 'c',
                            'channels': [{
                                'path': cls.channel,
                                'name': 'd'
                            }]
                        }]
                    }]
                }]
            }
        }

        # Make a dummy Core
        core = bfly.CoreLayer.Core(db)
        # Load the configuraton json files
        db.load_config(temp_config)

        # Get basic database keywords
        k_tables = cls.RUNTIME.DB.TABLE
        s_table = k_tables.SYNAPSE.NAME
        ####
        # S1 : is_synapse
        ####
        # Should all be true
        for syn in range(cls.s_count):
            args = s_table, cls.channel, syn
            res = db.get_entry(*args)
            # Raise exception if not true
            cls.assertTrue(not not res)
        # Should all be false
        for syn in range(cls.s_count, 2*cls.s_count):
            args = s_table, cls.channel, syn
            res = db.get_entry(*args)
            # Raise exception if not false
            cls.assertFalse(not not res)


    @classmethod
    def make_h5(cls):
        """ make a dummy h5 file for testing
        """
        # Get the datatype, noise range, and size
        dtype = getattr(np, 'uint{}'.format(cls.h_type))
        dmax = 2 ** cls.h_type
        dsize = cls.h_shape
        # Create the file from a path
        with h5py.File(cls.channel, 'w') as fd:
            # Make a random array
            pattern = randint(dmax, size= dsize, dtype= dtype)
            fd.create_dataset('stack', data= pattern)
        # Log that the file path was written
        cls._log('WRITE', path= cls.channel)

    @classmethod
    def make_dataset(cls):
        """ make dummy dataset files for database
        """
        k_files = cls.RUNTIME.DB.FILE
        #### 
        # Make blocks
        ####
        k_volume = k_files.BLOCK.BLOCK.NAME
        k_start = k_files.BLOCK.BOUND.START
        k_shape = k_files.BLOCK.BOUND.SHAPE
        # Pair the shape names with values
        shapes = zip(k_shape, cls.h_shape)
        # Get full bounds
        dmax = 2 ** cls.h_type
        bounds = {k: 0 for k in k_start}
        bounds.update({k:v for k,v in shapes})
        # Generate neuron list
        cls.neurons = choice(dmax, cls.n_count)
        pairs = zip(*[cls.neurons.tolist()]*2)
        # Make a random block file
        blocks = {
            k_volume : [bounds, pairs]
        }

        ####
        # Make synapses
        ####
        k_neurons = k_files.SYNAPSE.NEURON_LIST
        k_center = k_files.SYNAPSE.POINT.NAME
        k_shape = k_files.SYNAPSE.POINT.LIST
        # Take random pairs
        gen = cls.neurons, 2
        syn = range(cls.s_count)
        cells = [choice(*gen) for _ in syn]
        cells = np.uint32(cells).T.tolist()
        # Put pairs at random coordinates
        shapes = [cls.s_count, 3]
        coords = random(shapes)*cls.h_shape
        coords = np.uint32(coords).T.tolist()
        # Format neuron pairs and coordinates
        synapses = dict(zip(k_neurons, cells))
        synapses.update({
            k_center: dict(zip(k_shape, coords))
        })

        ####
        # Write blocks to file
        ####
        k_block = k_files.BLOCK.DEFAULT
        blockfile = os.path.join(cls.dataset, k_block)
        with open(blockfile, 'w') as bf:
            json.dump(blocks, bf)

        ####
        # Write synapses to file
        ####
        k_synapse = k_files.SYNAPSE.DEFAULT
        synapsefile = os.path.join(cls.dataset, k_synapse)
        with open(synapsefile, 'w') as sf:
            json.dump(synapses, sf)

    @classmethod
    def make_log(cls):
        """ make custom log for this test
        """
        utilities = bfly.UtilityLayer
        NamedStruct = utilities.NamedStruct
        NamelessStruct = utilities.NamelessStruct
        # Write all the formats for the logs
        formats = NamelessStruct(
            WRITE = NamedStruct('write',
                LOG = 'info',
                ACT = '''
||| Testing TestDatabase |||
The h5 file {path} is written.'''
            )
        )
        # Return the custom logging function
        return bfly.UtilityLayer.MakeLog(formats).logging

if __name__ == '__main__':
    ut.main()
