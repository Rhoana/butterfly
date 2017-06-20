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
    infile = "2017_06_20_x256_4096x4096.json"
    outfile = infile.replace('json','png')

    # Input files from the graph file   
    root_folder = '/n/coxfs01/thejohnhoffer/web_test'
    input_path = os.path.join(root_folder, infile)
    output_path = os.path.join(root_folder, outfile)

    def load_all(in_path):
        with open(in_path,'r') as fd:
            return json.load(fd)

    # Load all the input data from json
    all_data = load_all(input_path)

    # Get constants from first trial
    full_shape = all_data['shape']
    # Get all file and tile shapes in X
    tiles_x = all_data['tiles']
    # Get the average rates for each trial
    mean_rates = all_data['mean_rates']

    ##### 
    # Plot rate by h5 tile width
    # Plot lines for all file widths
    #####
    # Set up the plot
    fig, ax = plt.subplots()
    
    # Plot the rates for all tile shapes
    ax.plot(tiles_x, mean_rates)

    # Power of 2 X axis
    ax.set_xscale('log', basex=2)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

    # Label the graph
    plt.ylabel('Speed (MiB per second)')
    plt.xlabel('Tile size')
    title_fmt = 'Rate to serve {}x{} pixels'
    # Make a big title
    title_font = dict(fontsize=18)
    plt.title(title_fmt.format(*full_shape), **title_font)
    # Write to file
    plt.savefig(output_path)
