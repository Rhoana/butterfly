import NDA
import sys
import json
import numpy as np

class SynapseData():

    def __init__(self, connections):
        """
        Arguments
        ----------
        connections : str
            Path to synapse-connections.json file
        """
        # Read from synapse connections json file
        sdict = json.load(open(connections))
        n1, n2 = [np.uint32(sdict[k]) for k in "neuron_1", "neuron_2"]
        x, y, z = [np.uint32(sdict["synapse_center"][k]) for k in "xyz"]

        # Store the data for all synapses
        all_synapses = np.r_[n1, n2, x, y, z].T
        print all_synapses[:10]

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
    syn = SynapseData(SYNAPSE)
