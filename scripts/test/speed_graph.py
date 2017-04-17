import matplotlib.pyplot as plt
import numpy as np
import json

def n_key_filter(n, key):
    def trial_filter(trial):
        return n == np.prod(trial[key])
    return trial_filter

if __name__ == '__main__':

    full_shape = [8, 8192, 8192]
    in_fmt = 'speed_{}_{}_{}.json'
    in_file = in_fmt.format(*full_shape)

    # Load the model
    with open(in_file,'r') as fd:
        trials = json.load(fd)

    ##### 
    # TEST 1
    # Plot time by number of h5 files used
    # Plot lines for every different number of tiles
    #####
    fig, ax = plt.subplots()
    # Filter only for trials with files in one folder
    in_one_folder = n_key_filter(1, 'n_folders')
    one_folder = filter(in_one_folder, trials)
    # Filter for trials with 1, 8, 64, or 512 files
    for n_files in [1, 2, 4, 8, 16]:
        has_n_files = n_key_filter(n_files, 'n_files_zyx')
        n_file_dicts = filter(has_n_files, one_folder)
        # Now, get number of tiles and time
        def get_tile_times(d):
            n_tiles = np.prod(d['n_tiles_kji'])
            mean_time = d['mean_time']
            return [n_tiles, mean_time]
        tile_times = map(get_tile_times, n_file_dicts)
        cause, result = zip(*tile_times)
        ax.plot(cause, result, label = '{} files'.format(n_files))

    legend = ax.legend(loc='upper left')
    # Set the fontsize
    for label in legend.get_texts():
            label.set_fontsize('large')

    # Save to file
    plt.ylabel('time (seconds)')
    plt.xlabel('total number of tiles')
    title = 'time to load {}x{}x{} hdf5'.format(*full_shape)
    plt.title(title)
    plt.xscale('log', basex=2)
    plt.savefig('out.png')
