from CacheSource import CacheSource
from QueryLayer import TileQuery
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
        self._cache = CacheSource()

    def start_db(self, dname):
        return self.DB_CLASS()

    def get_data(self, query):
        image = self.find_tiles(query)
        return self.write_image(query, image)

    def find_tiles(self, query):
        q_type = query.dtype
        first_tile_index = query.tile_bounds[0]
        all_tiles = np.argwhere(np.ones(query.tile_shape))
        cutout = np.zeros(query.target_shape, dtype=q_type)
        tiles_needed = first_tile_index + all_tiles

        for t_index in tiles_needed:
            tile_crop = query.all_in_some(t_index)
            t_query = TileQuery(query, t_index, tile_crop)
            tile = self.load_tile(query, t_query)
            # Fill the tile into the full cutout
            to_cut = [t_query.target_origin, tile.shape]
            [Z0,Y0,X0],[Z1,Y1,X1] = query.some_in_all(*to_cut)
            cutout[Z0:Z1,Y0:Y1,X0:X1] = tile

        return np.moveaxis(cutout,0,-1)

    def load_tile(self, query, t_query):
        # Load from cache or from disk if needed
        cache_tile = self._cache.get_tile(query,t_query)
        if len(cache_tile):
            return cache_tile
        # Load from disk using source class
        source_class = t_query.source_class
        tile = source_class.load_tile(t_query)
        self._cache.add_tile(query,t_query,tile)
        return tile

    def write_image(self, query, vol):

        img_format = query.INPUT.IMAGE.FORMAT

        if img_format.VALUE in img_format.ZIP_LIST:
            output = StringIO.StringIO()
            volstring = vol[:,:,0].T.tostring('F')
            output.write(zlib.compress(volstring))
            return output.getvalue()

        if img_format.VALUE in img_format.TIF_LIST:
            output = StringIO.StringIO()
            tiffvol = vol[:,:,0]
            tifffile.imsave(output, tiffvol)
            return output.getvalue()

        image = cv2.imencode("." + img_format.VALUE, vol)
        return image[1].tostring()

    def get_info(self,query):
        return query.dump

    def update_feature(self, query, volume):
        return 0
    def read_feature(self, query):
        return ""
