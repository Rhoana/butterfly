from numpy.random import randint
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

class SpeedTestCutout(ut.TestCase):
    """ set up tests for `bfly.CoreLayer.Core` cutout logic
    """
    DB_PATH = None
    DB_TYPE = 'Zodb'
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

    def test_core(self):
        """ test that `bfly.Core` can start \
and successfully deliver tiles at a reasonable speed
        """

        # Log to command line
        logging.basicConfig(**self.log_info)
        # Make a custom log for this test
        self._log = self.make_log()

        # Make a data directory
        if not os.path.exists(self.dataset):
            os.makedirs(self.dataset)
        # Save a dummy h5 file
        self.make_h5()

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
                        'name': 'c',
                        'channels': [{
                            'path': self.channel,
                            'name': 'd'
                        }]
                    }]
                }]
            }]
        }
        # Make a dummy Core
        core = bfly.CoreLayer.Core(db)
        # Store the channel path
        db.load_config(temp_config)

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
        self._log('WRITE', path= self.channel)

    def make_log(self):
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
||| Testing SpeedTestCutout |||
The h5 file {path} is written.'''
            )
        )
        # Return the custom logging function
        return bfly.UtilityLayer.MakeLog(formats).logging

if __name__ == '__main__':
    ut.main()
