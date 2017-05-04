import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from glob import glob1
import numpy as np
import json
import os

if __name__ == '__main__':

    # Everything happens from this directory
    graph_dir = '/n/coxfs01/thejohnhoffer/h5_tiles/2017_05_03'

    # Load one trial
    def load_trial(in_file):
        in_path = os.path.join(graph_dir, in_file)
        with open(in_path,'r') as fd:
            return json.load(fd)
    # Load all the trials
    trials = map(load_trial, glob1(graph_dir,'*.json'))
    # Get constants from first trial
    t0 = trials[0]
    n_t = len(trials)
    full_shape = t0['full_shape']
    file_shapes = t0['file_shape']
    tile_shapes = t0['tile_shape']
    # Average the trials
    all_speeds = [t['mbps'] for t in trials]
    mean_speeds = np.mean(all_speeds, 0)

    ##### 
    # TEST 1
    # Plot Mbps over file x dimension
    #####
    # Fix a tile shape
    tile_id = 0
    tile_shape = tile_shapes[tile_id]
    # Set up the plot
    fig, ax = plt.subplots()
    # Get all file shape x values
    all_x = np.uint32(file_shapes).T[2]
    # Get all rate values
    all_r = mean_speeds.T[tile_id]
    ax.plot(all_x, all_r)

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
