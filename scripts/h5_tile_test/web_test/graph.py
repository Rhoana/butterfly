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

    # Get the file name
    infile = "2017_06_21_R0_500_jpg_x512_4096x4096.json"
    outfile = infile.replace('json','pdf')

    # Input files from the graph file   
    root_folder = '/n/coxfs01/thejohnhoffer/web_test'
    input_path = os.path.join(root_folder, infile)
    output_path = os.path.join(root_folder, outfile)

    def load_all(in_path):
        with open(in_path,'r') as fd:
            return json.load(fd)

    # Load all the input data from json
    all_data = load_all(input_path)
    # Set up the plot
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    for ploti in [0,1]:
        
        ax = axes[ploti]

        # Get constants from first trial
        full_shape = all_data['shape']
        # Get all file and tile shapes in X
        tiles_x = all_data['tiles']
        # Get the average rates for each trial
        mean_times = all_data['mean_times']
        # Get all the rates for each trial
        all_times = all_data['all_times']

        title_fmt = 'Time to serve full image'
        y_axis_label = 'Time (seconds)'
        y_format = '%.1f'

        ###
        # Get the number of tiles
        n_tiles = np.prod(full_shape / np.c_[tiles_x, tiles_x], 1)
        # Divide the total times by the number of tiles
        if ploti == 0:
            # Get the average and full time data
            mean_times = all_data['mean_times']
            all_times = all_data['all_times']
            # Change the type of the graph
            title_fmt = 'Mean time to serve one image tile'
            # Divide all the times by the number of tiles
            all_times = all_times / n_tiles[:,np.newaxis]
            mean_times = mean_times / n_tiles

        print mean_times
        ##### 
        # Plot rate by h5 tile width
        # Plot lines for all file widths
        #####
        # Limit y to zero
        ax.set_ylim(ymin = 0, ymax = 2)

        # Plot the rates for all tile shapes
        ax.plot(tiles_x, mean_times)

        # Line up all trial rates in a single list
        flat_times = np.array(all_times).flatten()
        # Copy the tiles to match the trial rates
        n_trials = int(len(flat_times) / len(tiles_x))
        flat_tiles = np.repeat(tiles_x, n_trials)

        # Plot the scatter plot
        ax.scatter(flat_tiles, flat_times)

        #ax.set_xscale('log', basex=2)
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.yaxis.set_major_formatter(FormatStrFormatter(y_format))

        # Power of 2 X axis
        ax.set_xticks(tiles_x)
        # Make a big title
        title_font = dict(fontsize=18)
        ax.set_title(title_fmt.format(*full_shape), **title_font)
        # Label the graph
        ax.set_xlabel('Tile size (side length in pixels)')
        ax.set_ylabel(y_axis_label)

    # Write to file
    plt.savefig(output_path)
