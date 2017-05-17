import os
import json
import rtree
import numpy as np

class RTreeDB():
    def __init__(self, file_name):

        # Basic parameters
        file_name = os.path.join(file_name, 'synapse')

        # Make a 3d index
        prop = rtree.index.Property()
        prop.idx_extension = 'index'
        prop.dat_extension = 'data'
        prop.dimension = 3

        # Write to the file name
        self._db = rtree.index.Index(file_name, properties = prop)

    def add_point(self, izyx):
        # Turn the point to a rectangle
        entry = np.tile(izyx[1:],2)
        # Separate the index
        index = izyx[0]
        # Insert the point into the tree
        self._db.insert(index, entry)

    def check_bounds(self, bounds):
        # Convert from [[z0,y0,x0], [z1,y1,x1]]
        # to [z0, y0, x0, z1, y1, x1]
        rect = np.uint32(bounds).flatten()
        # Get all ids in the bounds
        within = self._db.intersection(rect)
        return np.uint32(list(within))
