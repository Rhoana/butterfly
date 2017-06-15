import NDA
import sys
import json
import numpy as np

def synapse_data(connections):
    """
    Arguments
    ----------
    connections : str
        Path to synapse-connections.json file
    """
    # Read from synapse connections json file
    sdict = json.load(open(connections))
    n1, n2 = [np.uint64(sdict[k]) for k in "neuron_1", "neuron_2"]
    x, y, z = [np.uint64(sdict["synapse_center"][k]) for k in "xyz"]

    # Store the data for all synapses
    return np.c_[n1, n2, x, y, z]

def check_synapses(syn, nda):
    """ Check all synapses in syn against the nda
    """
    ERRORS = 0
    COUNT = 1000
    # Loop through all system synapses
    for id in range(len(syn)):
        # Get the file system and NDA data
        known, unknown = syn[id], nda.check_synapse(id)
        # Check if the known is the same as the unknown
        if not len(unknown) or np.any(known != unknown):
            msg = """
            Error for synapse {}!
        Expected {}
        NDA gave {}
            """.format(id, known, unknown)
            # Show an error
            print(msg)
            ERRORS += 1
        # Print nice percentages
        if id%100 == 0:
            msg = "{:d}%".format(100*id//COUNT)
            print(msg)
    msg = "Checked all synapses. Found {} errors.".format(ERRORS)
    print(msg)

if __name__ == "__main__":

    # The raw synapse data path on the file system
    SYNAPSE="/n/coxfs01/leek/results/2017-05-11_R0/synapse-connections.json"

    # The data as given by the NDA
    COLLECTION="team1_waypoint_201610_full_May6"
    EXPERIMENT="25k_201610_dataset"
    CHANNEL="segmentation_2_0_4"

    # Order the groups for the NDA
    GROUPS = [COLLECTION, EXPERIMENT, CHANNEL]
    # Get the username and password arguments
    USERNAME, PASSWORD = sys.argv[1:][:2]

    # Set up access to the NDA
    nda = NDA.NDA(GROUPS, USERNAME, PASSWORD)
    # Set up access to the file system
    syn = synapse_data(SYNAPSE)

    # Check all synapses
    check_synapses(syn, nda)
