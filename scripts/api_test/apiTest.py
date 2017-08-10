import os
import sys
import json
import numpy as np

# For python 2
import urllib2 as urllib

# For python 3
#from urllib import request as urllib

def format_url(server, full_size, group_list):

    # Format the URL for butterfly
    query_fmt = 'feature={}&id={}'
    shape_fmt = 'depth={}&height={}&width={}&x=0&y=0&z=0'.format(*full_size)
    group_fmt = 'experiment={}&sample={}&dataset={}&channel={}'.format(*group_list)
    return '{}/api/entity_feature?{}&{}&{}'.format(server, query_fmt, shape_fmt, group_fmt)

def get_all_neurons(_fmt):
    # Get all neurons
    all_string = urllib.urlopen(_fmt.format('all_neurons', 0)).read()
    return set( json.loads(all_string) )

def get_synapse_parent(_fmt, _id):
    # Get neurons linked to a synapse
    linked_string = urllib.urlopen(_fmt.format('synapse_parent', _id)).read()
    return set(json.loads(linked_string).values()) - set([_id])

def get_neuron_children(_fmt, _id):
    # Get synapses linked to a neuron
    linked_string = urllib.urlopen(_fmt.format('neuron_children', _id)).read()
    return set([ int(k) for k in json.loads(linked_string).keys() ])

def get_synapse_keypoint(_fmt, _id):
    # Get neurons linked to a neuron
    linked_string = urllib.urlopen(_fmt.format('synapse_keypoint', _id)).read()
    return json.loads(linked_string)

def get_shared_synapse(_syn_file):

    # Declare all parameters
    full_size= [3394, 26624, 26624]
    real_server = 'https://butterfly.rc.fas.harvard.edu'
    group_list = [
        'team1_waypoint_201610_full_May6',
        'team1_waypoint_201610_full_May6',
        '25k_201610_dataset',
        'em',
    ]
    fmt = format_url(real_server, full_size, group_list)
    # Output array
    all_shared = []

    with open(_syn_file, 'r') as jf:
        pairs = json.load(jf)

    for p in pairs:
        synapses = [get_neuron_children(fmt, i) for i in p]
        # Take the set union of the two synapse sets
        shared_set = synapses[0] & synapses[1]
        print ("""
        {} and {} share synapse {}
        """.format(p[0],p[1], shared_set))
        # Find the synapse keypoint for each of the shared synapses
        shared_keypoints = [get_synapse_keypoint(fmt, i) for i in shared_set]
        # Store to output
        coordinates = dict(zip(shared_set, shared_keypoints))
        all_shared.append(p + [coordinates])

    with open('out.json','w') as jf:
        json.dump(all_shared, jf)

def size_filter(count_file, count_min, banned_set=set()):
    """ Filter by size and number of synapses

    Arguments
    ----------
    count_file : str
        Path to file with id box-size on each line
    count_min : int
        The minimum number of boxes a neuron must cover
    banned_set : set
        The neurons never to use ever

    Returns
    --------
    list
        All neurons matching a given size
    """
    # Output
    out_list = []

    # If no file
    if not os.path.exists(count_file):
        return out_list

    # Load counts for all neurons
    all_counts = np.loadtxt(count_file, dtype=np.uint32)
    # Get indexes above threshold
    all_big = np.where(all_counts >= count_min)[0]
    return list(set(all_big) - banned_set)

def size_synapse_filter(count_file, count_min, banned_set=set(), two_way=False):
    """ Filter by size and number of synapses

    Arguments
    ----------
    count_file : str
        Path to file with id box-size on each line
    count_min : int
        The minimum number of boxes a neuron must cover
    banned_set : set
        The neurons never to use ever
    two_way : bool
        Whether linked neurons must also be >= min_size

    Returns
    --------
    dict
        Big neurons as keys with linked neurons as values
    """

    # Declare all parameters
    full_size= [1664, 14336, 14336]
    real_server = 'http://localhost:8487'
    group_list = [
        'R0',
        '2017_07_12',
        '50_50_50',
        'final_segmentation'
    ]
    # Get the URL to the butterfly instance
    fmt = format_url(real_server, full_size, group_list)
    # Output
    out_dict = {}

    # If no file
    if not os.path.exists(count_file):
        return out_dict

    # Load counts for all neurons
    all_counts = np.loadtxt(count_file, dtype=np.uint32)
    # Get indexes above threshold
    all_big = np.where(all_counts >= count_min)[0]
    all_big = list(set(all_big) - banned_set)

    # Check if each index has synapse
    for big_id in all_big:
        # Make some temporary sets
        this_id = set([big_id])
        these_ids = set()
        # Get all the synapses
        id_syns = get_neuron_children(fmt, big_id)
        # If there are synapses
        for syn_id in id_syns:
            # Get the neurons for the synapse
            syn_neurons = get_synapse_parent(fmt, syn_id) - this_id
            # Add the neuron to the final output
            if len(syn_neurons):
                new_id = list(syn_neurons)[0]
                # Check if meets size criteria
                if not two_way or new_id in all_big:
                    # Add to temp id set
                    these_ids.add(new_id)
        # Add set to dictionary if not empty
        if len(these_ids):
            out_dict[big_id] = list(these_ids)

    return out_dict 

if __name__ == "__main__":

    CASE = 0

    if CASE == 0:

        set_path = "/n/coxfs01/thejohnhoffer/R0/ids-2017-06-26_stitched/meshes/top_spread.txt"
        count_path = "/n/coxfs01/thejohnhoffer/R0/ids-2017-06-26_stitched/meshes/spread_count.txt"
        count_min = 20

        all_neurons = size_filter(count_path, count_min)
        # Write set
        with open(set_path, 'w') as sf:
            # Make set of all neurons
            sf.write(':'.join(map(str,all_neurons)))

        set_path = "/n/coxfs01/thejohnhoffer/R0/ids-2017-06-26_stitched/meshes/top_high.txt"
        count_path = "/n/coxfs01/thejohnhoffer/R0/ids-2017-06-26_stitched/meshes/high_count.txt"
        count_min = 7

        all_neurons = size_filter(count_path, count_min)
        # Write set
        with open(set_path, 'w') as sf:
            # Make set of all neurons
            sf.write(':'.join(map(str,all_neurons)))

        sys.exit()


    # DEFAULT CASE

    out_path = "/n/coxfs01/thejohnhoffer/R0/ids-2017-07-12_final/meshes/big_linked_nodes.json"
    set_path = "/n/coxfs01/thejohnhoffer/R0/ids-2017-07-12_final/meshes/big_linked_nodes.txt"
    count_path = "/n/coxfs01/thejohnhoffer/R0/ids-2017-07-12_final/meshes/spread_count.txt"
    banned_set = set([418327,224632])
    count_min = 4
    two_way = True

    # Get big neurons with synapses
    neuron_dict = size_synapse_filter(count_path, count_min, banned_set, two_way) 
    
    # Write out
    with open(out_path, 'w') as jf:
        json.dump(neuron_dict, jf, indent=4)

    # Write set
    with open(set_path, 'w') as sf:
        # Make set of all neurons
        all_neurons = set(neuron_dict.keys())
        for n_val in neuron_dict.values():
            all_neurons = all_neurons | set(n_val)
        # Make into a string 
        all_neurons = list(all_neurons)
        sf.write(':'.join(map(str,all_neurons)))
