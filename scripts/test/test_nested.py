from numpy.random import randint
import numpy as np
import json
import h5py
import time
import os

class Maker():
    def __init__(self, size, dtype):
        self.size = size
        self.dtype = dtype

    def make(self, filedata):
        filename = filedata['path']
        # Make the parent directory
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Get the datatype, noise range, and size
        dtype = getattr(np, 'uint{}'.format(self.dtype))
        dmax = 2 ** self.dtype
        dsize = self.size
        # Create the file from a path
        with h5py.File(filename, 'w') as fd:
            # Make a random uint array
            pattern = randint(dmax, size= dsize, dtype= dtype)
            fd.create_dataset('stack', data= pattern)

class Hasher():
    def __init__(self):
        self.offsets = []
    @property
    def shape(self):
        max_offset = np.max(self.offsets,0)
        return (max_offset + 1)

    def hash(self, hashed, filedata):
        offset = filedata['offset']
        # Track all the offsets
        self.offsets.append(offset)
        # Map the offset to the path
        hashed[str(offset)] = filedata['path']
        return hashed

class Tester():
    def __init__(self, files, zyx_shape, kji_shape):
        self.zyx_shape = np.array(zyx_shape)
        self.kji_shape = np.array(kji_shape)
        self.int_shape = np.uint32(kji_shape)
        self.files = files

    def load(self, path, start):
        with h5py.File(path, 'r') as fd:
            dataset = fd[fd.keys()[0]]
            k0,j0,i0 = start
            k1,j1,i1 = start + np.uint32(self.int_shape)
            v = dataset[k0:k1,j0:j1,i0:i1]

    def test(self, kji):
        # Get xyz tile file
        kji_full = kji * self.kji_shape
        zyx = np.floor(kji_full / self.zyx_shape)
        zyx_full = np.uint32(zyx * self.zyx_shape)
        # Get file path and file start
        file_key = str(list(np.uint32(zyx)))
        file_path = self.files.get(file_key)
        if not file_path:
            raise AttributeError
        file_start = np.uint32(kji_full - zyx_full)
        # Load file from path and start
        self.load(file_path, file_start)

def main(in_file, trials, full_shape, block_shape):
    # Load the model
    with open(in_file,'r') as fd:
        listed = json.load(fd)

    # Hash the files
    hasher = Hasher()
    model = reduce(hasher.hash, listed, {})
    tile_shape = np.uint32(hasher.shape)

    # Get the tile shape
    zyx_shape = full_shape / tile_shape
    # Get the block shape
    kji_shape = zyx_shape / block_shape
    dtype = 8

    # Make the files
    make = Maker(zyx_shape, dtype)
    map(make.make, listed)

    # Get all kji blocks
    kji_range = full_shape // kji_shape
    kji_count = np.prod(tile_shape*block_shape)
    # Ensure consistencey
    if np.prod(kji_range) != kji_count:
        return {}
    # Get all the block indexes
    all_kji = zip(*np.where(np.ones(kji_range)))

    # Test the files
    time_results = []
    test = Tester(model, zyx_shape, kji_shape)
    # Run the testing
    for t in range(trials):
        time_start = time.time()
        map(test.test, all_kji)
        time_end = time.time()
        # Record time difference
        time_diff = time_end - time_start
        time_results.append(time_diff)

    return {
        'time': time_results,
        'mean_time': float(np.mean(time_results)),
        'zyx_shape': map(int, zyx_shape),
        'kji_shape': map(int, kji_shape),
        'n_files_zyx': map(int, tile_shape),
        'n_tiles_kji': map(int, kji_range),
        'in_file': str(in_file),
    }


if __name__ == '__main__':

    block_shape = [1, 2, 2]
    in_file = 'dataset.json'
    full_shape = np.uint32([20, 10000, 10000])

    main(in_file, full_shape, block_shape)


