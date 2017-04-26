import matplotlib.pyplot as plt
from glob import glob1
import numpy as np
import json
import os

if __name__ == '__main__':

    # Everything happens from this directory
    graph_dir = 'results/2017_04_25'

    # Load one case
    def load_case(in_file):
        in_path = os.path.join(graph_dir, in_file)
        with open(in_path,'r') as fd:
            return json.load(fd)
    # Load all the cases
    cases = map(load_case, glob1(graph_dir,'*.json'))
    # Get the first full shape
    full_shape = cases[0]['full_shape']

    ##### 
    # TEST 1
    # Plot Mbps over file x dimension
    #####
    # Fix a tile shape
    tile_shape = np.uint32([1, 32, 32])
    tile_x = tile_shape[-1]
    # Set up the plot
    fig, ax = plt.subplots()
    # Get a size,rate pair
    def get_pair(d):
        return map(d.get, ['file_x', 'mbps'])
    # Limit to cases with same tile_shape
    def is_tile(d):
        d_tile = d['tile_shape']
        return np.any(tile_shape == d_tile)
    # Filter all cases for same tile_shape
    tile_cases = filter(is_tile, cases)
    # Get the size,rate pairs for all cases
    tile_rates = map(get_pair, tile_cases)
    all_tr = np.uint32(tile_rates)
    # Plot the lists sorted by file sizes
    tr_order = all_tr.T[0].argsort()
    ax.plot(*all_tr[tr_order].T)

    # Label the graph
    plt.ylabel('Speed (MiB per second)')
    plt.xlabel('width of partial hdf5 files')
    title_fmt = 'Rate to load {}x{}x{} voxels'
    sub_fmt = 'in blocks of {}x{}x{} pixels'
    # Make a big title with a subtitle
    small = dict(fontsize=14)
    big = dict(fontsize=18)
    plt.suptitle(title_fmt.format(*full_shape), **big)
    plt.title(sub_fmt.format(*tile_shape), **small)
    # Write to file
    plt.savefig('out.png')
