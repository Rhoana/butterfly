from Settings import MAX_CACHE_SIZE
from pylru import lrucache
import numpy as np

class CacheEntry(object):
    max_size = MAX_CACHE_SIZE
    def __init__(self, query, n_entry):
        each_size = np.prod(query.blocksize)
        each_bytes = query.dtype(0).itemsize
        self.each = each_size*each_bytes
        self.query = query
        # update max entries and create tile cache
        max_entry = self.update_size(n_entry)
        self._tiles = lrucache(max_entry)

    @property
    def loaded_source(self):
        output = self.query.OUTPUT.INFO
        runtime = self.query.RUNTIME.IMAGE
        return {
            output.TYPE.NAME: output.TYPE.VALUE,
            runtime.BLOCK.NAME: runtime.BLOCK.VALUE,
            output.SIZE.NAME: output.SIZE.VALUE
        }

    def update_size(self, n_entry):
        my_max_size = self.max_size/n_entry
        max_entry = int(my_max_size/self.each)
        if hasattr(self,'_tiles'):
            self._tiles.size(max_entry)
        return max_entry

    def add_tile(self, t_query, content):
        self._tiles[t_query.key] = content
        return self.get_tile(t_query)

    def get_tile(self, t_query):
        return self._tiles.get(t_query.key, [])

