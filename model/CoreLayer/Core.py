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
        image_ids = self.find_tiles(query)
        # Load from cache or from disk if needed
        tiles = self.load_tiles(query, image_ids)
        return write_tiles(query, tiles)

    def find_tiles(self, query):
        box_start, box_end = query.indexed_bounds
        index_grid = np.ones(box_end - box_start)
        offsets_needed = np.argwhere(index_grid)
        tiles_needed = offsets_needed+box_start

        cutshape = query.blocksize*index_grid.shape
        cutout = np.zeros(cutshape, dtype=self.dtype)
        fixed = [query.z, query.scale]
        for tile_index in tiles_needed:
            offset = query.index_offset(tile_index)
            [i0,j0] = query.blocksize*(offset)
            [i1,j1] = query.blocksize*(offset+1)
            one_tile = list(tile_index)+fixed
            tile = self.load(*one_tile)
            cutout[j0:j1,i0:i1] = tile

        x0y0,x1y1 = query.scaled_bounds
        origin = box_start * query.blocksize
        left,top = (x0y0 - origin).astype(int)
        right,down = (x1y1 - origin).astype(int)
        return cutout[top:down,left:right]

    def load_tiles(self, query, im_ids):
        all_tiles = [load_tile(query,im) for im in im_ids]
        return self.write_tiles(query, im_ids, all_tiles)

    def load_tile(self, t_id):
        cache_tile = self._cache.load_image(query,t_id)
        if len(cache_tile):
            return cache_tile
        source_class = tile_id['disk_format']
        tile = source_class.load_tile(tile_id)
        self._cache.add_image(query,t_id,tile)
        return tile

    def write_tiles(self, query, im_ids, tiles):
        return ""

    def get_json(self,query):
        return '[test]'

    def update_feature(self, query, volume):
        return 0
    def read_feature(self, query):
        return ""
