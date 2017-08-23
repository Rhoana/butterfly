from MakeData import full_path
from MakeData import write_synapses
from MakeData import write_neurons
from MakeData import make_neurons
from MakeData import make_synapses
from MakeData import make_centers
import unittest as ut
import logging as log
import numpy as np
import bfly
import sys

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
        channel_path = full_path('data/channel.h5')
        data_path = full_path('data')
        # shape, and type for temp file
        zyx_shape = [250, 2500, 2500]
        ids_info = np.iinfo(np.uint32)
        zyx_info = np.iinfo(np.uint32)

        # Make neurons
        neuron_ids, other_ids = make_neurons(neuron_n, ids_info, neuron_seed)
        neuron_centers = make_centers(neuron_n, zyx_shape, zyx_info, neuron_seed)
        # Make synapses
        synapse_pairs = make_synapses(synapse_n, neuron_ids, ids_info, synapse_seed)
        synapse_centers = make_centers(synapse_n, zyx_shape, zyx_info, synapse_seed)
        # Get constants for input files
        k_files = self.RUNTIME.DB.FILE
        # Save synapse-connections.json
        write_synapses(k_files, data_path, synapse_pairs, synapse_centers)
        # Save neuron-soma.json
        write_neurons(k_files, data_path, neuron_ids, neuron_centers)

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
                        'path': data_path,
                        'name': 'c',
                        'channels': [{
                            'path': channel_path,
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
        n_table = k_tables.NEURON.NAME

        ####
        # S1 : is_synapse
        ####
        msg = "is_synapse: ID {} returns {}"
        # Should be synapses
        for syn in range(0, synapse_n):
            res = db.is_synapse(s_table, channel_path, syn)
            self.assertTrue(res, msg.format(syn, res))
        # Should not be synapses
        for syn in range(synapse_n, 2*synapse_n):
            res = db.is_synapse(s_table, channel_path, syn)
            self.assertFalse(res, msg.format(syn, res))
        ####
        # S5 : is_neuron
        ####
        msg = "is_neuron: ID {} returns {}"
        # Should be neruons
        for nrn in neuron_ids:
            res = db.is_neuron(n_table, channel_path, nrn)
            self.assertTrue(res, msg.format(nrn, res))
        # Should not be neurons
        for nrn in other_ids:
            res = db.is_neuron(n_table, channel_path, nrn)
            self.assertFalse(res, msg.format(nrn, res))

        # Get the list of keys for coordinates
        k_axes = k_tables.ALL.POINT_LIST
        MAX_SCALE = 10
        ####
        # S3 : synapse_keypoint
        ####
        msg = """synapse_keypoint: id {0} returns {1}={2}.
        It should have {1}={3} at scale {4}.
        """
        # Should match centers
        for syn, cen in enumerate(synapse_centers):
            # Use an arbitrary scale
            scale = 2 ** (syn % MAX_SCALE)
            center = cen // [1, scale, scale]
            result = db.synapse_keypoint(s_table, channel_path, syn, scale)
            # Error checker
            def asserter(i):
                real = center[i]
                axis = k_axes[i]
                res = result[axis]
                # Assert result has real value
                error = msg.format(syn, axis, res, real, scale)
                self.assertEqual(res, real, error)
            # Assert all axes are expected
            map(asserter, range(3))
        ####
        # S7 : neuron_keypoint
        ####
        msg = """neuron_keypoint: id {0} returns {1}={2}.
        It should have {1}={3} at scale {4}.
        """
        # Should match centers
        for nrn, cen in zip(neuron_ids, neuron_centers):
            # Use an arbitrary scale
            scale = 2 ** (nrn % MAX_SCALE)
            center = cen // [1, scale, scale]
            result = db.neuron_keypoint(n_table, channel_path, nrn, scale)
            # Error checker
            def asserter(i):
                real = center[i]
                axis = k_axes[i]
                res = result[axis]
                # Assert result has real value
                error = msg.format(nrn, axis, res, real, scale)
                self.assertEqual(res, real, error)
            # Assert all axes are expected
            map(asserter, range(3))

        k_links = self.RUNTIME.FEATURES.LINKS
        k_sides = [k_links.PRE.NAME, k_links.POST.NAME]
        ####
        # S3 : synapse_parent
        ####
        msg = """synapse_parent: id {0} returns {1}={2}.
        It should have {1}={3}.
        """
        for syn, pair in enumerate(synapse_pairs):
            result = db.synapse_parent(s_table, channel_path, syn)
            # Error checker
            def asserter(i):
                real = pair[i]
                side = k_sides[i]
                res = result[side]
                # Assert result has real value
                error = msg.format(syn, side, res, real)
                self.assertEqual(res, real, error)
            # Assert all axes are expected
            map(asserter, range(2))
        ####
        # S8 : neuron_children
        ####
        msg = """synapse_parent: id {0} in synapse {1} is {2}.
        Id {0} should be {3} for this synapse.
        """
        k_kinds = ['none','first','second','both']
        for nrn in neuron_ids:
            start = [0,0,0]
            stop = zyx_shape
            result = db.neuron_children(s_table, channel_path, nrn, start, stop)
            # Check all child synapses
            for syn, kind in result.items():
                pair = synapse_pairs[syn]
                # Get the real and resulting labels
                real_kind = sum(np.where(pair == nrn)[0]+1)
                real_label = k_kinds[real_kind]
                res_label = k_kinds[kind]
                # Assert both labels are equal
                error = msg.format(nrn, syn, res_label, real_label)
                self.assertEqual(res_label, real_label, error)

if __name__ == '__main__':
    ut.main()
