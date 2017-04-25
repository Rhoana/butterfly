import matplotlib.pyplot as plt
import numpy as np
import json

if __name__ == '__main__':

    full_shape = [1, 16384, 16384]
    in_fmt = 'graph_{}_{}_{}.json'
    in_file = in_fmt.format(*full_shape)

    # Load the model
    with open(in_file,'r') as fd:
        cases = json.load(fd)

    ##### 
    # TEST 1
    # Plot Mbps over file x dimension
    #####
    # Fix a tile shape
    tile_shape = [1, 32, 32]
    tile_x = tile_shape[-1]
    # Set up the plot
    fig, ax = plt.subplots()
    # Limit the Ge
    # Get a size,rate pair
    def get_pair(d):
        return map(d.get, ['file_x', 'mbps'])
    # Get the size,rate pairs for all cases
    tile_rates = map(get_pair, tile_cases)
    # Plot list of rates over list of file sizes
    ax.plot( *zip(*tile_rates) )

    # Label the graph
    plt.ylabel('Speed (MiB per second)')
    plt.xlabel('width of partial hdf5 files')
    title_fmt = 'Rate to load {}x{}x{} voxels'
    sub_fmt = 'in blocks of {}x{}x{} pixels'
    # Make a big title with a subtitle
    small = dict(fontsize=14)
    big = dict(y=1.05, fontsize=18)
    plt.title(sub_fmt.format(*tile_shape), **small)
    plt.suptitle(title_fmt.format(*full_shape), **big)
    # Write to file
    plt.savefig('out.png')
