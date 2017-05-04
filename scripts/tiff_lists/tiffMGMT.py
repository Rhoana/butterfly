import os
import json
import h5py
import time
import argparse
import numpy as np
import tifffile as tiff

class TiffMGMT():
    ALL = 'tiles'
    PATH = 'location'
    ZYX = ['z','row','column']

    def __init__(self, in_path):
        """ Load the json file
        
        Arguments
        ----------
        in_path : str
            The path to the json file
        """
        with open(in_path, 'r') as jd:
            # Get all the filenames
            boss_file = json.load(jd)
            all = boss_file.get(self.ALL, []) 
            # Get all the paths
            def get_path(d):
                return d.get(self.PATH, '')
            all_path = map(get_path, all)
            # Get all the offsets
            def get_offset(d):
                return map(d.get, self.ZYX)
            # Get the offsets and the max offset
            all_off = np.uint32(map(get_offset, all))
            self.size = np.amax(all_off, 0) + 1
            # Get the xy dimensions and product
            self.size_xy = np.uint32(self.size[1:])
            self.n_xy = np.prod(self.size_xy)
            # Get the tile size from first tile
            tile0 = tiff.imread(all_path[0])
            self.tile_shape = np.uint32((1,) + tile0.shape)
            # The size and datatype of the full volume
            self.full_shape = self.tile_shape * self.size
            self.slice_shape = self.tile_shape[1:][np.newaxis]
            self.dtype = tile0.dtype
            # Sort all paths by ordered offsets
            def make_flat(pair):
                return np.ravel_multi_index(pair[0], self.size)
            # Sort paths by ordered offsets
            pairs = sorted(zip(all_off, all_path), key=make_flat)
            self.all_off, self.all_path = zip(*pairs)
            self.all_off = np.uint32(self.all_off)

    def scale_h5(self, _bounds, _path, _res):
        """ Return a list of unique ids in a bounding box
        
        Arguments
        ----------
        _bounds : numpy.ndarray
            2x1 array of scaled z_arg bounds
        _path : str
            The path to the output h5 file
        _res : int
            Number of times to downsample by 2
        """
        # Downsampling constant
        scale = 2 ** _res
        # Get the downsampled full / tile shape
        scale_bounds = _bounds // scale
        scale_full = self.full_shape // scale
        scale_tile = self.tile_shape // scale
        scale_tile = np.clip(scale_tile, 1, scale_full)
        # Prepare the downsampled h5 file
        all_keys = {
            'shape': scale_full,
            'dtype': self.dtype,
            'chunks': tuple(scale_tile),
        }
        print("""
Writing {} volume to {}
""".format(scale_full, _path))
        # Start timing the h5 file writing
        sec_start = time.time()
        # Create the file from a path
        with h5py.File(_path, 'w') as fd:
            # Make the output dataset 
            a = fd.create_dataset('all', **all_keys)
            # Add to the h5 file for the given stack
            for s_z in range(*scale_bounds):
                # Scale the z bound
                z = s_z * scale
                # Open all tiff files in the stack
                for f in range(self.n_xy):
                    # Get tiff file path and offset
                    f_id = int(z * self.n_xy + f)
                    f_path = self.all_path[f_id]
                    f_offset = self.all_off[f_id]
                    # Read the file to a numpy volume
                    f_vol = tiff.imread(f_path)
                    scale_vol = f_vol[::scale,::scale]
                    # Get coordinates to fill the tile
                    y0, x0 = scale_tile[1:] * f_offset[1:]
                    y1, x1 = [y0, x0] + np.uint32(scale_vol.shape)
                    # Fill the tile with scaled volume
                    a[s_z, y0:y1, x0:x1] = scale_vol

                print("""
            Added layer {} to h5 file
            """.format(z))
        # Record total writing time
        sec_diff = time.time() - sec_start
        print("""
Wrote {} layers to {} in {} seconds
""".format(len(scale_bounds), _path, sec_diff))


    def bound_set(self, bounds):
        """ Return a list of unique ids in a bounding box
        
        Arguments
        ----------
        bounds : numpy.ndarray
            3x2 array of z_arg, y_arg, and x_arg bounds
        """
