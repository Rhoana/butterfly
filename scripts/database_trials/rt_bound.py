import json
import time
import argparse
import numpy as np
from rtreedb import RTreeDB

def parse_args():

    help = {
        'rt_bound': 'test limits of rtree',
        'f': 'path to create an rtree file',
        'start': 'comma separated start',
        'stop': 'comma separated stop',
    }

    parser = argparse.ArgumentParser(help['rt_bound'])
    parser.add_argument('-f', default='database', help=help['f'])
    parser.add_argument('start', help=help['start'])
    parser.add_argument('stop', help=help['stop'])

    # Return parsed dictionary
    return vars(parser.parse_args())

if __name__ == '__main__':

    # Get argument dictionary
    argd = parse_args()
    # Make the database
    db = RTreeDB(argd['f'])
    # Get the start and stop bounds
    start = np.uint32(argd['start'].split(','))
    stop = np.uint32(argd['stop'].split(','))
    # Start timing rtree lookup
    t0 = time.time()
    # Check against the rtree
    in_bounds = db.check_bounds([start, stop])
    t1 = time.time()
    # Print time taken to check bounds
    print("""{}

    in {:.2f} seconds
    """.format(in_bounds, t1-t0))
