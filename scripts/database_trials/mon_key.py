import json
import time
import argparse
import numpy as np
from mongodb import MongoDB

def parse_args():

    help = {
        'mon_key': 'read single value from mongodb',
        'key': 'integer synapse id to read',
        'port': 'port for the database',
    }

    parser = argparse.ArgumentParser(help['mon_key'])
    parser.add_argument('key', type=int, help=help['key'])
    parser.add_argument('-p', type=int, default=27017, help=help['port'])

    # Return parsed dictionary
    return vars(parser.parse_args())

if __name__ == '__main__':

    # Get argument dictionary
    argd = parse_args()
    # Make the database
    key = argd['key']
    db = MongoDB(argd['p'])
    # Start timing mongo lookup
    t0 = time.time()
    # Read the value from mongo db
    in_bounds = db.check_key(key)
    t1 = time.time()
    # Print time taken to check bounds
    print("""{}

    in {:.2f} seconds
    """.format(in_bounds, t1-t0))
