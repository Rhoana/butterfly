from CacheSource import CacheSource
from QueryLayer import TileQuery
from DatabaseLayer import *
from ImageLayer import *
import numpy as np

class Core(object):
    dnames = {
        'mongo': Mongo
    }
    sources = {
        'hdf5': HDF5(),
        'mojo': Mojo(),
        'stack': ImageStack(),
        'specs': TileSpecs()
    }
    basic = {
        'source': 'stack',
        'dname': 'mongo'
    }
    def __init__(self, dname):
        self._database = self.start_db(dname)
        self._cache = CacheSource()

    def start_db(self, dname):
        dbclass = self.dnames.get(dname, self.basic['dname'])
        return dbclass()

    def get_data(self, query):
        image = self.find_tiles(query)
        return write_image(query, image)

    def find_tiles(self, query):
        q_type = query.dtype
        first_tile_index = query.tiled_bounds[0]
        all_tiles = np.argwhere(np.ones(query.tiled_shape))
        cutout = np.zeros(query.scaled_shape, dtype=q_type)
        tiles_needed = first_tile_index + all_tiles

        for t_index in tiles_needed:
            tile_crop = query.all_in_some(t_index)
            [X0, Y0],[X1, Y1] = query.some_in_all(t_index)
            one_tile = TileQuery(query, t_index, *tile_crop)
            tile = self.load_tile(query, one_tile)
            cutout[Y0:Y1,X0:X1] = tile

        return cutout

    def load_tile(self, query, t_id):
        # Load from cache or from disk if needed
        cache_tile = self._cache.get_tile(query,t_id)
        if len(cache_tile):
            return cache_tile
        source_class = getattr(t_id,t_id.DISK)
        tile = source_class.load_tile(t_id)
        self._cache.add_tile(query,t_id,tile)
        return tile

    def write_image(self, query, volume):
        return ""

    def get_info(self,query):
        return query.dump

    def update_feature(self, query, volume):
        return 0
    def read_feature(self, query):
        return ""
