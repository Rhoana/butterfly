import os
import cv2
import json
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
            # Get the tile size from first tile
            tile0 = tiff.imread(all_path[0])
            self.tile_shape = tile0.shape    
            # Get all the offsets
            def get_offset(d):
                off_3d = map(d.get, self.ZYX)
            all_off = map(get_offset, all)
            # Flatten offsets by max offset
            max_off = np.amax(all_off, 0)
            print max_off
            import ipdb; ipdb.set_trace()

            #print all_off

    def set_bound(self, bounds):
        """ Return a list of unique ids in a bounding box
        
        Arguments
        ----------
        bounds : numpy.ndarray
            3x2 array of z_arg, y_arg, and x_arg bounds
        """

