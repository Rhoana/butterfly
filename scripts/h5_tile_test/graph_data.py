import matplotlib
matplotlib.use('Agg')
from matplotlib.ticker import FormatStrFormatter
import matplotlib.pyplot as plt
from glob import glob1
import numpy as np
import time
import json
import os

PLOT = 3

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
    files_x = np.uint64(t0['file_shape']).T[-1]
    tiles_x = np.uint64(t0['tile_shape']).T[-1]
    # Average the trials
    all_speeds = [t['mbps'] for t in trials]
    mean_speeds = np.mean(all_speeds, 0)
    # Average the times
    all_times = [t['seconds'] for t in trials]
    mean_times = np.mean(all_times, 0)
    # To numpy array
    all_speeds = np.array(all_speeds)
    # TEMP
    #mean_speeds /= 8

    if PLOT == 0:
        ##### 
        # Plot rate by h5 tile width
        # Plot lines for all file widths
        #####
        # Set up the plot
        fig, ax = plt.subplots(figsize=(10, 5))
        for file_i, file_x in enumerate(files_x):
            # Get rates for given file shape
            file_rates = mean_speeds[file_i, :]

            # Find only where values are nonzero
            real_rates = np.nonzero(file_rates)[0]
            if not len(real_rates) > 1:
                continue
            # Filter tiles_x and rates by nonzero
            real_tiles_x = tiles_x[real_rates]
            real_tiles_r = file_rates[real_rates]
            # Plot the rates for this tile shape
            file_label = '{}px file size'.format(file_x)
            ax.plot(real_tiles_x, real_tiles_r, label=file_label)

        # Power of 2 X axis
        ax.set_xscale('log', basex=2)
    #    ax.set_yscale('log', basey=2)
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # Set the legend fontsize
        legend = ax.legend(loc='lower right')
        for label in legend.get_texts():
            label.set_fontsize('large')

        # Label the graph
        plt.ylabel('Speed (MiB per second)')
        plt.xlabel('Tile size')
        title_fmt = 'Rate to load {}x{} pixels'
        # Make a big title
        title_font = dict(fontsize=18)
        plt.title(title_fmt.format(*full_shape[-2:]), **title_font)
        # Write to file
        plt.savefig('out.pdf')

    elif PLOT == 1:
        ##### 
        # Plot rate by h5 file width
        # Plot lines for all tile widths
        #####
        # Get the file counts from file sizes
        files_x = np.prod(full_shape) / np.square(files_x)

        # Set up the plot
        fig, ax = plt.subplots(figsize=(8, 5))
        for tile_i, tile_x in enumerate(tiles_x):
            # Get rates for given tile shape
            tile_rates = mean_speeds[:, tile_i]

            if tile_x > 4096 or tile_x < 512:
                continue

            # Find only where values are nonzero
            real_rates = np.nonzero(tile_rates)[0]
            if not len(real_rates) > 1:
                continue

            # Filter tiles_x and rates by nonzero
            real_files_x = files_x[real_rates]
            real_files_r = tile_rates[real_rates]

            # Plot the rates for this tile shape
            tile_label = '{}px tile size'.format(tile_x)
            ax.plot(real_files_x, real_files_r, marker='o', label=tile_label)

        # Power of 2 X axis
        ax.set_xscale('log', basex=2)
    #    ax.set_yscale('log', basey=2)
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # Set the legend fontsize
        legend = ax.legend(loc='upper left')
        for label in legend.get_texts():
            label.set_fontsize('large')

        # Force only relevant ticks
        plt.xticks(files_x[:-2]) 

        # Label the graph
        plt.ylabel('Speed (MiB per second)')
        plt.xlabel('Number of files')
        title_fmt = 'Rate to load full section'
        # Make a big title
        title_font = dict(fontsize=18)
        plt.title(title_fmt, **title_font)
        # Write to file
        plt.savefig('out.pdf')

    elif PLOT == 2:
        ##### 
        # Plot rate by h5 file width
        # Plot one line for max tile widths
        #####

        # Set up the plot
        fig, ax = plt.subplots(figsize=(10, 5))
        # Get corresponding indices
        tiles_i = enumerate(tiles_x)
        tiles_i = [(ti, t) for ti, t in tiles_i if t in files_x]
        ft = [(list(files_x).index(t),ti) for ti, t in tiles_i]
        # Get all rates
        ft_rate = [mean_speeds[fi, ti] for fi, ti in ft]

        # Reverse tile sizes for legend clarity
        reverse_tiles = list(enumerate(tiles_x))[::-1]

        for tile_i, tile_x in reverse_tiles:
            # Get rates for given tile shape
            tile_rates = mean_speeds[:, tile_i]

            if tile_x > 4096 or tile_x < 512:
                #pass
                continue

            # Find only where values are nonzero
            real_rates = np.nonzero(tile_rates)[0]
            if not len(real_rates) > 1:
                continue

            # Filter tiles_x and rates by nonzero
            real_files_c = files_c[real_rates]
            real_files_r = tile_rates[real_rates]

            # Plot the rates for this tile shape
            tile_label = '{} pixel tiles'.format(tile_x)
            ax.plot(real_files_c, real_files_r, label=tile_label, marker='o')

       
        # Plot the rates for the maximum tile shapes by file size
        tile_label = 'one tile per file'
        ax.plot(ft_count[:-3], ft_rate[:-3], label=tile_label, color='black', ls='--')

        # Power of 2 X axis
        ax.set_xscale('log', basex=2)
    #    ax.set_yscale('log', basey=2)
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # Set the legend fontsize
        legend = ax.legend(loc='upper left')
        for label in legend.get_texts():
            label.set_fontsize('large')

        # Force only relevant ticks
        plt.xticks(files_c[:]) 
        #ax.set_xlim(xmax = files_c[-3]) 

        # Label the graph
        plt.ylabel('Speed (MiB per second)')
        plt.xlabel('Number of files')
        title_fmt = 'Bit rate to read files'
        # Make a big title
        title_font = dict(fontsize=18)
        plt.title(title_fmt, **title_font)
        # Write to file
        plt.savefig('out.pdf')

    else:
        ##### 
        # Plot rate by h5 tiles per file
        # Plot one line for max tile widths
        #####

        # Set up the plot
        fig, ax = plt.subplots(figsize=(10, 5))

        # Reverse tile sizes for legend clarity
        reverse_tiles = list(enumerate(tiles_x))[::-1]

        for tile_i, tile_x in reverse_tiles:
            # Get rates for given tile shape
            tile_times = mean_speeds[:, tile_i]
            tile_dots = all_speeds[:,:, tile_i]

            if tile_x > 4096 or tile_x < 512:
                continue

            # Find only where values are nonzero
            real_rates = np.nonzero(tile_times)[0]
            if not len(real_rates) > 1:
                continue

            # Filter tiles_x and rates by nonzero
            real_files_x = files_x[real_rates]
            real_times = tile_times[real_rates]

            # Get tiles per file
            real_ratios = np.square(real_files_x / tile_x)
            # Limit to first four ratios
            real_ratios = real_ratios[:4]
            real_times = real_times[:4]

            # Scatter plot prep
            real_dots = tile_dots.T[real_rates][:4].T
            real_dot_ratios = np.uint64([real_ratios,]*len(real_dots))

            dot_color = 'crgb'[tile_i]
            ax.scatter(real_dot_ratios[:], real_dots[:], s=4, color=dot_color)

            # Plot the rates for this tile shape
            tile_label = '{} pixel tiles'.format(tile_x)
            ax.plot(real_ratios, real_times, label=tile_label, marker='o')

        # Power of 2 X axis
        ax.set_xscale('log', basex=2)
    #    ax.set_yscale('log', basey=2)
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

        # Set the legend fontsize
        legend = ax.legend(loc='upper right')
        for label in legend.get_texts():
            label.set_fontsize('large')

        # Force only relevant ticks
        tick_ratios = (2**(np.arange(4)))**2
        plt.xticks(tick_ratios) 
        #ax.set_xlim(xmax = files_c[-3]) 

        # Label the graph
        plt.ylabel('Speed (MiB per second)')
        plt.xlabel('Number of tiles per file')
        title_fmt = 'Bit rate to read files'
        # Make a big title
        title_font = dict(fontsize=18)
        plt.title(title_fmt, **title_font)
        # Write to file
        plt.savefig('out.pdf')
