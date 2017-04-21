import bfly
import numpy as np
from numpy.random import randint
import unittest as ut
import datetime
import logging
import h5py
import sys

class SpeedTestCutout(ut.TestCase):
    """ set up tests for `bfly.CoreLayer.Core` cutout logic
    """
    DB_PATH = None
    DB_TYPE = 'Zodb'
    # path, shape, and type for temp file
    # THIS FILE PATH SHOULD NOT EXIST
    h_path = 'tests/data/25k_noise.h5'
    h_shape = [1, 25000, 25000]
    # uint 8, 16, or 32
    h_type = 8
    RUNTIME = bfly.UtilityLayer.RUNTIME()
    # Log to the command line
    log_info = {
        'stream': sys.stdout,
        'level': logging.INFO
    }

    @classmethod
    def test_core(cls):
        """ test that `bfly.Core` can start \
and successfully deliver tiles at a reasonable speed
        """

        # Log to command line
        logging.basicConfig(**cls.log_info)
        # Make a custom log for this test
        cls._log = cls.make_log()

        # Save a dummy h5 file
        cls.make_h5()

        # Make a dummy database
        db_class = getattr(bfly.DatabaseLayer, cls.DB_TYPE)
        db = db_class(cls.DB_PATH, cls.RUNTIME)
        # Add a dummy config to a dummy database
        # TODO

        # Make a dummy Core
        core = bfly.CoreLayer.Core(db)

    @classmethod
    def make_h5(cls):
        """ make a dummy h5 file for testing
        """
        # Get the datatype, noise range, and size
        dtype = getattr(np, 'uint{}'.format(cls.h_type))
        dmax = 2 ** cls.h_type
        dsize = cls.h_shape
        # Create the file from a path
        with h5py.File(cls.h_path, 'w') as fd:
            # Make a random uint8 array
            pattern = randint(dmax, size= dsize, dtype= dtype)
            fd.create_dataset('stack', data= pattern)
        # Log that the file path was written
        cls._log('WRITE', path= cls.h_path)

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
||| Testing SpeedTestCutout |||
The h5 file {path} is written.'''
            )
        )
        # Return the custom logging function
        return bfly.UtilityLayer.MakeLog(formats).logging

if __name__ == '__main__':
    ut.main()
