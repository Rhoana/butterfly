import json
import time
import argparse
import numpy as np
from mongodb import MongoDB

def generate_synapses(_count):

    # All sides same in fictional volume
    side_length = 512000
    dtype = np.uint32
    # Make _count rows of 3 coordinates
    shape = [_count, 3]
    synapses = np.random.randint(0, side_length, shape, dtype)

    # Just get coordinates
    return synapses

def parse_args():

    help = {
        'mon_gen': 'add random values to mongodb',
        'port': 'port for the database',
        'count': 'number of synapses to generate',
    }

    parser = argparse.ArgumentParser(help['mon_gen'])
    parser.add_argument('count', type=int, help=help['count'])
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
    all_entries = generate_synapses(argd['count'])
    t1 = time.time()
    print('generated synapses in {:.2f} sec'.format(t1-t0))

    # add all entries
    db.add_points(all_entries)
    t2 = time.time()
    print('wrote db in {:.2f} sec'.format(t2-t1))
