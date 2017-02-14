from DatabaseLayer import *
from ImageLayer import *
from Cache import Cache

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
        self._cache = Cache()

    def start_db(self, dname):
        dbclass = self.dnames.get(dname, self.basic['dname'])
        return dbclass()

    def get_data(self, query):
        image = self.find_tiles(query)
        return write_image(query, image)

    def find_tiles(self, query):
        box = query.indexed_bounds
        box_start, box_end = np.split(box, 2)
        index_grid = np.ones(box_end - box_start)
        tiles_needed = np.argwhere(index_grid) + box_start

        # all tiles loaded at full size in cutout
        full_shape = query.blocksize * index_grid.shape
        cutout = np.zeros(full_shape, dtype=self.dtype)
        always_same = [query.z, query.scale]
        for tile_index in tiles_needed:
            tile_bounds = query.tile_bounds(tile_index)
            x0, y0, x1, y1 = query.scale_offset(tile_bounds)
            one_tile = Image_ID(tile_index, *always_same)
            tile = self.load_tile(one_tile)
            cutout[y0:y1,x0:x1] = tile

        all_bounds = query.scaled_bounds
        X0, Y0, X1, Y1 = query.scale_offset(all_bounds)
        return cutout[Y0:Y1, X0:X1]

    def load_tile(self, t_id):
        # Load from cache or from disk if needed
        cache_tile = self._cache.get_tile(query,t_id)
        if len(cache_tile):
            return cache_tile
        source_class = tile_id['disk_format']
        tile = source_class.load_tile(tile_id)
        self._cache.add_tile(query,t_id,tile)
        return tile

    def write_image(self, query, volume):
        return ""

    def get_json(self,query):
        return '[test]'

    def update_feature(self, query, volume):
        return 0
    def read_feature(self, query):
        return ""
