import json
import time
import argparse
import numpy as np
from rtreedb import RTreeDB

def load_synapses(_path):

    # Load the file with the synapses
    with open(_path, 'r') as f:
	all_dict = json.load(f)
	point_dict = all_dict['synapse_center']

    # Transpose the list of all synapses
    links = map(all_dict.get, ['neuron_1', 'neuron_2'])
    center = map(point_dict.get, ['z', 'y', 'x'])
    synapses = np.uint32(links + center).T

    # Just get coordinates
    keys = range(len(synapses))
    return np.c_[keys, synapses[:,2:]]

def parse_args():

    help = {
        'rt_import': 'test limits of rtree',
        'f': 'path to create an rtree file',
        'path': 'path to synapse-connections.json',
    }

    parser = argparse.ArgumentParser(help['rt_import'])
    parser.add_argument('-f', default='database', help=help['f'])
    parser.add_argument('path', help=help['path'])

    # Return parsed dictionary
    return vars(parser.parse_args())

if __name__ == '__main__':

    # Get argument dictionary
    argd = parse_args()
    # Make the database
    db = RTreeDB(argd['f'])

    # Parse the entries
    t0 = time.time()
    all_entries = load_synapses(argd['path'])
    t1 = time.time()
    print('read json in {:.2f} sec'.format(t1-t0))

    # add all entries
    for entry in all_entries:
        db.add_point(entry)
    t2 = time.time()
    print('wrote db in {:.2f} sec'.format(t2-t1))
