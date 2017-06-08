from functools import partial
import numpy as np
import time
import math
import h5py
import json
import sys
import os

MEM_LIMIT = 1000
MEGA = 1000**2

def load_h(_size, _path, _start):
    # Start timing now
    start = time.time()
    # Load a tile from a path
    with h5py.File(_path, 'r') as fd:
        d = fd[fd.keys()[0]]
        # Get subvolume in d
        z0, y0, x0 = _start
        z1, y1, x1 = _start + _size
        subvol = d[z0:z1, y0:y1, x0:x1]
    # Return the time difference
    return time.time() - start

def make_h(_type, _size, _path):
    # Get the datatype, noise range, and size
    dtype = getattr(np, 'uint{}'.format(_type))
    slice_size = np.uint32(_size[1:])
    dmax = 2 ** _type
    # Calculate the max area for a section
    max_area = MEM_LIMIT * (8*MEGA) / _type
    this_area = float(np.prod(slice_size))
    # Get the tile shape that fits in memory
    over_area = max(this_area / max_area, 1)
    tile_size = slice_size / math.sqrt(over_area)
    tile_size = np.uint32(np.floor(tile_size))
    # Get all the positions of tiles needed
    tile_ratio = slice_size / np.float64(tile_size)
    i_shape = np.uint32(np.ceil(tile_ratio))
    i_range = np.uint32(range(np.prod(i_shape)))
    all_tiles = np.unravel_index(i_range, i_shape)
    all_tiles = np.uint32(all_tiles).T
    # Get keywords for file and slice
    chunk_size = (1,) + tuple(tile_size)
    all_keys = dict(shape= _size, dtype= dtype, chunks=chunk_size)
    z_keys = dict(size= tile_size, dtype= dtype)
    # Create the file from a path
    with h5py.File(_path, 'w') as fd:
        # Make a random uint array
        a = fd.create_dataset('all', **all_keys)
        # Fill each z step of that array
        for z in range(int(_size[0])):
            # Fill in each tile of that array
            for yx in all_tiles:
                # Get data to fill the tile
                y1,x1 = np.clip(tile_size*(yx+1), 0, slice_size)
                y0,x0 = tile_size*(yx)
                # Fill the tile specifically
                z_keys['size'] = [y1-y0,x1-x0]
                a_tile = np.random.randint(dmax, **z_keys)
                # Print writing this tile
                print("""writing {}, {}, {}
                """.format(z, y0, x0).replace('\n', ''))
                sys.stdout.flush()
                # Write tile to volume
                a[z,y0:y1,x0:x1] = a_tile

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
            # Writing the full file
            print("""
Writing file {}""".format(f_n))
            sys.stdout.flush()
            # Write the full file
            make_h(int_type, _shape, f_n)
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
            # Written the full file
            print("""
Loading file {}""".format(f_n))
            sys.stdout.flush()
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
    noise_fmt = '/n/regal/pfister_lab/thejohnhoffer/h5_noise/{}/{}'
    noise_dir = noise_fmt.format(exp, trial_id)
    # Make the temporary directory
    if not os.path.exists(noise_dir):
        try:
            os.makedirs(noise_dir)
        except OSError:
            pass

    # Set the full shape and file sizes
    full_shape = np.uint32([1, 2**14, 2**14])
    file_divs = np.uint32([
      [1,1,1],
      [1,2,2],
      [1,4,4],
      [1,8,8],
      [1,16,16],
      [1,32,32],
      [1,64,64],
      [1,128,128],
      [1,256,256],
    ])
    # Get the number of files
    file_counts = np.prod(file_divs, 1)
    # Get the shapes of all the files
    file_sizes = full_shape / file_divs
    # Set the tile sizes, trial count, and datatype
    tile_sizes = np.uint32([
      [1, 32, 32],
      [1, 64, 64],
      [1, 128, 128],
      [1, 512, 512],
      [1, 1024, 1024],
    ])
    trial_start = 0
    int_type = 8
    # Get the total mebibytes
    full_bytes = int_type * np.prod(full_shape)
    full_mb = int(full_bytes / (1024 ** 2))

    # Get the file / tile indexes for the array id
    id_shape = [len(file_sizes), len(tile_sizes)]
    id_range = range(np.prod(id_shape))

    # record times for all trials
    trial_times = np.zeros(id_shape)
    trial_rates = np.zeros(id_shape)

    # Random list of file names
    total_files = np.sum(file_counts) * id_shape[1]
    chosen = np.random.choice(10**9, int(total_files))
    file_names = map('noise_{:09d}.h5'.format, chosen)

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
    graph_file = '{:04d}.json'.format(trial_start + trial_id)
    graph_file = os.path.join(graph_dir, graph_file)

    # Write the model to json
    with open(graph_file, 'w') as fd:
        json.dump(graph_data, fd, indent=4)
