import numpy as np
unknown = ['datapath','blocksize','disk_format']

class CacheSource(object):
    def __init__(self):
        self._tileSource = []
        self.query = None

    def add_tile(self, id, content):
        return np.zeros([2,2])

    def get_tile(self, id):
        return np.zeros([2,2])

    def lose_tile(self, id):
        return 0

    def lose_all(self):
        return 0

