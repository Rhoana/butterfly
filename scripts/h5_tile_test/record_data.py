from functools import partial
import tifffile as tiff
import numpy as np
import time
import math
import json
import sys
import os

MEM_LIMIT = 1000
MEGABYTE = 1024**2

def load_h(_size, _path, _start):
    # Start timing now
    start = time.time()
    # Load a tile from a path
    d = tiff.imread(_path)
    # Get subvolume in d
    y0, x0 = _start
    y1, x1 = _start + _size
    subvol = d[y0:y1, x0:x1]
    # Return the time difference
    return time.time() - start

def make_h(_bytes, _size, _path):
    # Get number of bits
    n_bits = 8 * _bytes
    # Get the datatype, noise range, and size
    dtype = getattr(np, 'uint{}'.format(n_bits))
    slice_size = np.uint32(_size)
    dmax = 2 ** n_bits
    # Get keywords for random noise
    noise_keys = dict(size= slice_size, dtype= dtype)
    # Make a random uint array
    a_tile = np.random.randint(dmax, **noise_keys)
    # Write tile to volume
    tiff.imsave(_path, a_tile)

class Manager():
    def __init__(self, _dir, _names):
        self._dir = _dir
        # Add the output dir to all the names
        join_dir = partial(os.path.join, _dir)
        self._names = list(map(join_dir, _names))

    def make_all(self, _count, _shape):
        #####
        # Make all the folder's files
        #####
        # Take some random file names
        f_names = self._names[:_count]
        del self._names[:_count]
        # Make files for all file names
        for f_n in f_names:
            # Write the full file
            make_h(voxel_bytes, _shape, f_n)
        # Return file names
        return f_names

    @staticmethod
    def load_all(_fsize, _tsize, _files):
        # Get the tile offsets in every source file
        t_offs = np.where(np.ones(_fsize / _tsize))
        offsets = _tsize * np.uint32(t_offs).T
        # Track the total time
        timed = 0
        # Load all files
        for f_n in _files:
            # Load all for this file name
            load_fn = partial(load_h, _tsize, f_n)
            # Add the time to load one file
            timed += sum(map(load_fn, offsets))
        # Return time to load all files
        return timed

    def rm_all(self):
        # Remove all files in directory
        for _name in self._names:
            if os.path.exists(_name):
                try:
                    os.remove(_name)
                except OSError:
                    print("""
                    Could not remove {}
                    """.format(_name))
                    sys.stdout.flush()

    def trial(self, f_c, f_s, t_s):
        # Remove all files
        self.rm_all()
        # Make all the folder's files
        f_names = self.make_all(f_c, f_s)
        # Load all the folder's files
        timed = self.load_all(f_s, t_s, f_names)
        # Return trial time
        return timed


if __name__ == '__main__':

    # Get the global array index
    trial_id = 0
    if len(sys.argv) > 1:
        trial_id = int(sys.argv[1])

    # Get the size of the volume
    full_scale = 14
    if len(sys.argv) > 2:
        full_scale = int(sys.argv[2])

    # Get the minimum tile and file size
    min_tile_scale = 9
    min_file_scale = 9
    
    # Get the number of bytes per voxel
    voxel_bytes = 1
    if len(sys.argv) > 3:
        voxel_bytes = int(sys.argv[3])

    # Output files go to the graph dir   
    graph_fmt = '/n/coxfs01/thejohnhoffer/2017/butterfly/scripts/h5_tile_test/results/{}'
    exp = os.getenv('H5_EXPERIMENT', time.strftime('%Y_%m_%d'))
    graph_dir = graph_fmt.format(exp)
    # Make the working directory
    if not os.path.exists(graph_dir):
        try:
            os.makedirs(graph_dir)
        except OSError:
            pass

    # Temp files go to the noise_dir
    noise_fmt = '/n/coxfs01/thejohnhoffer/h5_noise/{}/{}'
    noise_dir = noise_fmt.format(exp, trial_id)
    # Make the temporary directory
    if not os.path.exists(noise_dir):
        try:
            os.makedirs(noise_dir)
        except OSError:
            pass

    # Set the full shape
    full_width = 2 ** full_scale
    full_shape = np.uint32([full_width, full_width])
    print("full shape {}".format(full_shape))
    # Get the range of scales
    tile_scales = range(min_tile_scale, full_scale+1)
    #tile_scales = range(10, 12)

    file_scales = range(min_file_scale, full_scale+1)
    # Set the tile sizes and file sizes
    tile_sizes = np.uint32([(2**i,)*2 for i in tile_scales])
    file_sizes = np.uint32([(2**i,)*2 for i in file_scales])
    # Get the number of files
    file_counts = np.prod(full_shape / file_sizes, 1)

    print """
      tile sizes: 
        {}
      file sizes:
        {}
      file counts: {}
    """.format(tile_sizes, file_sizes, file_counts)
    # Get the total mebibytes
    full_bytes = voxel_bytes * np.prod(full_shape)
    full_mb = int(full_bytes / MEGABYTE)

    # Get the file / tile indexes for the array id
    id_shape = [len(file_sizes), len(tile_sizes)]
    id_range = range(np.prod(id_shape))

    # record times for all trials
    trial_times = np.zeros(id_shape)
    trial_rates = np.zeros(id_shape)

    # Random list of file names
    total_files = np.sum(file_counts) * id_shape[1]
    chosen = np.random.choice(10**9, int(total_files))
    file_names = map('noise_{:09d}.tiff'.format, chosen)

    # Loop through all combinations of tile and file shapes
    for f_id, t_id in zip(*np.unravel_index(id_range, id_shape)):

        # Get the file size, file count, and tile size
        t_s = tile_sizes[t_id]
        f_s = file_sizes[f_id]
        f_c = file_counts[f_id]

        # Continue if tile size > file size
        if np.any(t_s > f_s):
          msg = """***********************
      Cannot load files of {}px in {}px blocks
      """.format(f_s, t_s)
          print(msg)
          continue

        # Get all the needed file names
        f_names = map(file_names.pop, range(f_c)[::-1])
        # Manage output directory and file names
        mgmt = Manager(noise_dir, f_names)

        # Get the time to load the shape
        trial_time = mgmt.trial(f_c, f_s, t_s)
        trial_rate = -1
        if trial_time:
            trial_rate = full_mb / trial_time
        # Add the time to the output
        trial_times[f_id, t_id] = trial_time
        trial_rates[f_id, t_id] = trial_rate

        msg = """***********************
    Loaded all {} files of {}px
    in blocks of {}px at {:.1f}Mbps
    """.format(f_c, f_s, t_s, trial_rate)
        print(msg)
        sys.stdout.flush()

    # Give feedback
    graph_data = {
        'n_files': file_counts.tolist(),
        'tile_shape': tile_sizes.tolist(),
        'file_shape': file_sizes.tolist(),
        'full_shape': full_shape.tolist(),
        'seconds': trial_times.tolist(),
        'mbps': trial_rates.tolist(),
    }
    # The file for the graph
    graph_file = '{:04d}.json'.format(trial_id)
    graph_file = os.path.join(graph_dir, graph_file)

    # Write the model to json
    with open(graph_file, 'w') as fd:
        json.dump(graph_data, fd, indent=4)
