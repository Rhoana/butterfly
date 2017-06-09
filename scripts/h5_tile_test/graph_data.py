import matplotlib
matplotlib.use('Agg')
from matplotlib.ticker import FormatStrFormatter
import matplotlib.pyplot as plt
from glob import glob1
import numpy as np
import time
import json
import os

if __name__ == '__main__':

    # Input files from the graph dir   
    graph_fmt = '/n/coxfs01/thejohnhoffer/2017/butterfly/scripts/h5_tile_test/results/{}'
    exp = os.getenv('H5_EXPERIMENT', time.strftime('%Y_%m_%d'))
    graph_dir = graph_fmt.format(exp)

    # Load one trial
    def load_trial(in_file):
        in_path = os.path.join(graph_dir, in_file)
        with open(in_path,'r') as fd:
            return json.load(fd)
    # Load all the trials
    trials = map(load_trial, glob1(graph_dir,'*.json'))

    # Get constants from first trial
    t0 = trials[0]
    full_shape = t0['full_shape']
    # Get all file and tile shapes in X
    files_x = np.uint32(t0['file_shape']).T[-1]
    tiles_x = np.uint32(t0['tile_shape']).T[-1]
    # Average the trials
    all_speeds = [t['mbps'] for t in trials]
    mean_speeds = np.mean(all_speeds, 0)

    ##### 
    # Plot rate by h5 file width
    # Plot lines for all tile widths
    #####
    # Set up the plot
    fig, ax = plt.subplots()
    for tile_i, tile_x in enumerate(tiles_x):
        # Get rates for given tile shape
        tile_rates = mean_speeds[:, tile_i]

        # Plot the rates for this tile shape
        tile_label = '{}px tile width'.format(tile_x)
        ax.plot(files_x, tile_rates, label=tile_label)

    # Power of 2 X axis
    ax.set_xscale('log', basex=2)
    ax.set_yscale('log', basey=2)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

    # Set the legend fontsize
    legend = ax.legend(loc='upper left')
    for label in legend.get_texts():
        label.set_fontsize('large')

    # Label the graph
    plt.ylabel('Speed (MiB per second)')

    # Set the legend fontsize
    legend = ax.legend(loc='upper left')
    for label in legend.get_texts():
        label.set_fontsize('large')

    # Label the graph
    plt.ylabel('Speed (MiB per second)')
    plt.xlabel('width of partial hdf5 files')
    title_fmt = 'Rate to load {}x{}x{} voxels'
    # Make a big title
    title_font = dict(fontsize=18)
    plt.title(title_fmt.format(*full_shape), **title_font)
    # Write to file
    plt.savefig('out.png')
