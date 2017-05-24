import json
import time
import argparse
import numpy as np
from mongodb import MongoDB

def load_synapses(_path):

    # Load the file with the synapses
    with open(_path, 'r') as f:
	all_dict = json.load(f)
	point_dict = all_dict['synapse_center']

    # Transpose the list of all synapses
    centers = map(point_dict.get, ['z', 'y', 'x'])
    synapses = np.uint32(centers).T

    # Just get coordinates
    return synapses

def parse_args():

    help = {
        'mon_import': 'import json file into mongodb',
        'path': 'path to synapse-connections.json',
        'port': 'port for the database',
    }

    parser = argparse.ArgumentParser(help['mon_import'])
    parser.add_argument('path', help=help['path'])
    parser.add_argument('-p', type=int, default=27017, help=help['port'])

    # Return parsed dictionary
    return vars(parser.parse_args())

if __name__ == '__main__':

    # Get argument dictionary
    argd = parse_args()
    # Make the database
    db = MongoDB(argd['p'])
    # Clear database
    db.reset()
    print('cleared database')

    # Parse the entries
    t0 = time.time()
    all_entries = load_synapses(argd['path'])
    t1 = time.time()
    print('read json in {:.2f} sec'.format(t1-t0))

    # add all entries
    db.add_points(all_entries)
    t2 = time.time()
    print('wrote db in {:.2f} sec'.format(t2-t1))
