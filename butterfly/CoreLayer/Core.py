from Cache import Cache
from QueryLayer import TileQuery
from QueryLayer import DataQuery
from DatabaseLayer import *
import numpy as np
import tifffile
import StringIO
import zlib
import cv2

class Core(object):
    DB_CLASS = Mongo

    def __init__(self, dname):
        self._database = self.start_db(dname)
        self._cache = Cache()

    def start_db(self, dname):
        return self.DB_CLASS()

    def update_feature(self, query, volume):
        return 0

    def read_feature(self, query):
        return ""

    '''
    All methods to load data
    '''

    def get_info(self, i_query):
        d_query = self.make_data_query(i_query)
        keywords = self.update_query(d_query)
        i_query.update_source(keywords)
        return i_query.dump

    def get_data(self, query):
        self.update_query(query)
        image = self.find_tiles(query)
        return self.write_image(query, image)

    def find_tiles(self, query):
        first_tile_index = query.tile_bounds[0]
        all_tiles = np.argwhere(np.ones(query.tile_shape))
        cutout = np.zeros(query.target_shape, query.dtype)
        tiles_needed = first_tile_index + all_tiles

        for t_index in tiles_needed:
            # Make a query for the given tile
            t_query = self.make_tile_query(query, t_index)
            tile = self.load_tile(query, t_query)
            # Fill the tile into the full cutout
            to_cut = [t_query.target_origin, tile.shape]
            [Z0,Y0,X0],[Z1,Y1,X1] = query.some_in_all(*to_cut)
            cutout[Z0:Z1,Y0:Y1,X0:X1] = tile

        return cutout

    def make_data_query(self, i_query):
        # Begin building needed keywords
        i_path = i_query.OUTPUT.INFO.PATH

        return DataQuery(**{
            i_query.INPUT.METHODS.NAME: 'data',
            i_path.NAME: i_path.VALUE
        })

    def make_tile_query(self, query, t_index):
        tile_crop = query.all_in_some(t_index)
        return TileQuery(query, t_index, tile_crop)

    def update_query(self, query):
        cache_entry = self._cache.get_source(query)
        if not cache_entry:
            # Create a preporatory tile_query
            t0_index = np.uint32([0,0,0])
            t0_query = self.make_tile_query(query, t0_index)
            keywords = t0_query.preload_source
        else:
            keywords = cache_entry.loaded_source
        # Update current query with preloaded terms
        query.update_source(keywords)
        self._cache.add_source(query)
        return keywords

    def load_tile(self, query, t_query):
        # grab request size for query
        t_bounds = t_query.target_bounds
        (K0,J0,I0),(K1,J1,I1) = t_bounds-t_bounds[0]

        # Load from cache or from disk if needed
        cache_tile = self._cache.get_tile(query,t_query)
        if len(cache_tile):
            return cache_tile[K0:K1,J0:J1,I0:I1]
        # Load from disk 
        tile = t_query.tile

        self._cache.add_tile(query,t_query,tile)

        return tile[K0:K1,J0:J1,I0:I1]

    def write_image(self, query, vol):

        img_format = query.INPUT.IMAGE.FORMAT

        if img_format.VALUE in img_format.ZIP_LIST:
            output = StringIO.StringIO()
            volstring = vol[0].T.tostring('F')
            output.write(zlib.compress(volstring))
            return output.getvalue()

        if img_format.VALUE in img_format.TIF_LIST:
            output = StringIO.StringIO()
            tiffvol = vol[0]
            tifffile.imsave(output, tiffvol)
            return output.getvalue()

        filetype = "." + img_format.VALUE
        image = cv2.imencode(filetype, vol[0])
        return image[1].tostring()
