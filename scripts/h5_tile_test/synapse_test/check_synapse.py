import NDA
import sys

if __name__ == "__main__":

    COLLECTION="team1_waypoint_201610_full_May6"
    EXPERIMENT="25k_201610_dataset"
    CHANNEL="segmentation_2_0_4"

    # Order the groups for the NDA
    GROUPS = [COLLECTION, EXPERIMENT, CHANNEL]
    # Get the username and password arguments
    USERNAME, PASSWORD = sys.argv[1:][:2] 

    # Set up access to the NDA
    nda = NDA.NDA(GROUPS, USERNAME, PASSWORD)

    nda.is_synapse(0)
