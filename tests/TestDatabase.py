from MakeData import full_path
from MakeData import write_synapses
from MakeData import write_neurons
from MakeData import make_neurons
from MakeData import make_synapses
from MakeData import make_centers
from MakeData import make_bounds
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
        synapse_ids = np.arange(synapse_n, dtype=ids_info.dtype)
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
        for syn in synapse_ids:
            res = db.is_synapse(s_table, channel_path, syn)
            self.assertTrue(res, msg.format(syn, res))
        # Should not be synapses
        for syn in range(synapse_ids[-1]+1, 2*synapse_n):
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
        msg = """synapse_keypoint: ID {0} returns {1}={2}.
        It should have {1}={3} at scale {4}.
        """
        # Should match centers
        for syn, cen in zip(synapse_ids, synapse_centers):
            # Use an arbitrary scale
            scale = 2 ** (syn % MAX_SCALE)
            center = cen // [1, scale, scale]
            result = db.synapse_keypoint(s_table, channel_path, syn, scale)
            # Error checker
            def asserter(i):
                ideal = center[i]
                axis = k_axes[i]
                res = result[axis]
                # Assert result has ideal value
                error = msg.format(syn, axis, res, ideal, scale)
                self.assertEqual(res, ideal, error)
            # Assert all axes are expected
            map(asserter, range(3))
        ####
        # S7 : neuron_keypoint
        ####
        msg = """neuron_keypoint: ID {0} returns {1}={2}.
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
                ideal = center[i]
                axis = k_axes[i]
                res = result[axis]
                # Assert result has ideal value
                error = msg.format(nrn, axis, res, ideal, scale)
                self.assertEqual(res, ideal, error)
            # Assert all axes are expected
            map(asserter, range(3))

        k_links = self.RUNTIME.FEATURES.LINKS
        k_sides = [k_links.PRE.NAME, k_links.POST.NAME]
        ####
        # S3 : synapse_parent
        ####
        msg = """synapse_parent:
        ID {0} shows a {1} of {2}, but
        ID {0} should have {1} of {3}.
        """
        for syn, pair in zip(synapse_ids, synapse_pairs):
            result = db.synapse_parent(s_table, channel_path, syn)
            # Error checker
            def asserter(i):
                ideal = pair[i]
                side = k_sides[i]
                res = result[side]
                # Assert result has ideal value
                error = msg.format(syn, side, res, ideal)
                self.assertEqual(res, ideal, error)
            # Assert all axes are expected
            map(asserter, range(2))
        ####
        # S8 : neuron_children
        ####
        msg = """neuron_children:
        In bounds from {4} to {5},
        ID {0} has \033[91m{2}\033[0m part of synapse {1}, but
        ID {0} should have \033[92m{3}\033[0m part of synapse {1}.
        """
        # Keywords for logging
        k_words = ['no','the 1st','the 2nd','each']
        # Check for all neurons
        for nrn in neuron_ids:
            # Get all synapses with neuron
            is_nrn = synapse_pairs == nrn
            is_syn = is_nrn.any(1)
            ideal_nrn = is_nrn[is_syn]*[1,2]
            # Get synapse relations to neuron
            ideal_ids = synapse_ids[is_syn]
            ideal_kinds = np.sum(ideal_nrn, 1)
            ideal_centers = synapse_centers[is_syn]
            # Combine ids with kind of relation
            ideal_syns = np.c_[ideal_ids, ideal_kinds]
            # Error checker
            def asserter(start, stop):
                # Get ideal values within bounds
                above = ideal_centers >= start
                below = ideal_centers < stop
                # Get synapse ids and kinds 
                bound = (above & below).all(1)
                ideal = dict(ideal_syns[bound])
                # Get results from the database
                res = db.neuron_children(s_table, channel_path, nrn, start, stop)
                # Test all keys in ideal or result
                for syn in set(ideal.keys()) | set(res.keys()):
                    # Get both keywords
                    res_word = k_words[res.get(syn, 0)]
                    ideal_word = k_words[ideal.get(syn, 0)]
                    # Assert both labels are equal
                    error = msg.format(nrn, syn, res_word, ideal_word, start, stop)
                    self.assertEqual(res_word, ideal_word, error)

            # Test whole image and random bounds
            any_bounds = make_bounds(zyx_shape, zyx_info, nrn)
            asserter([0,0,0], zyx_shape)
            asserter(*any_bounds)

if __name__ == '__main__':
    ut.main()
