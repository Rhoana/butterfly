import os
import json
import pymongo
import numpy as np

class MongoDB():
    def __init__(self, file_name):
        pass

    def add_point(self, izyx):
        # Turn the point to a rectangle
        entry = np.tile(izyx[1:],2)
        # Separate the index
        index = izyx[0]
        # Insert the point into the tree
        #self._db.insert(index, entry)

    def check_key(self, key):
        pass
