import json

# For python 2
import urllib2 as urllib

# For python 3
#from urllib import request as urllib

def format_url(server, full_size, group_list):

    # Format the URL for butterfly
    query_fmt = 'feature={}&id={}'
    shape_fmt = 'depth={}&height={}&width={}&x=0&y=0&z=0'.format(*full_size)
    group_fmt = 'experiment={0}&sample={0}&dataset={1}&channel={2}'.format(*group_list)
    return '{}/api/entity_feature?{}&{}&{}'.format(server, query_fmt, shape_fmt, group_fmt)

def get_all_neurons(_fmt):
    # Get all neurons
    all_string = urllib.urlopen(_fmt.format('all_neurons',0)).read()
    return set( json.loads(all_string) )

def get_neuron_children(_fmt, _id):
    # Get neurons linked to a neuron
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

