import json
import time
import argparse
import numpy as np
from rtreedb import RTreeDB

def generate_synapses(_count):

    # All sides same in fictional volume
    side_length = 512000
    dtype = np.uint32
    # Make _count rows of 3 coordinates
    shape = [_count, 3]
    synapses = np.random.randint(0, side_length, shape, dtype)

    # Just get coordinates
    keys = range(_count)
    return np.c_[keys, synapses]

def parse_args():

    help = {
        'rt_import': 'test limits of rtree',
        'f': 'path to create an rtree file',
        'count': 'number of synapses to generate',
    }

    parser = argparse.ArgumentParser(help['rt_import'])
    parser.add_argument('-f', default='database', help=help['f'])
    parser.add_argument('count', type=int, help=help['count'])

    # Return parsed dictionary
    return vars(parser.parse_args())

if __name__ == '__main__':

    # Get argument dictionary
    argd = parse_args()
    # Make the database
    db = RTreeDB(argd['f'])

    # Parse the entries
    t0 = time.time()
    all_entries = generate_synapses(argd['count'])
    t1 = time.time()
    print('generated synapses in {:.2f} sec'.format(t1-t0))

    # add all entries
    for entry in all_entries:
        db.add_point(entry)
    t2 = time.time()
    print('wrote db in {:.2f} sec'.format(t2-t1))
