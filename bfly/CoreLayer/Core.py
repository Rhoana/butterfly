from AccessLayer.QueryLayer import TileQuery
from AccessLayer.QueryLayer import DataQuery
from Cache import Cache
import numpy as np
import tifffile
import StringIO
import zlib
import cv2

class Core(object):

    def __init__(self, db):
        # Get DB Terms
        self._db = db
        RUNTIME = db.RUNTIME

        # Make Cache with keywords
        self._cache = Cache(RUNTIME)

    '''
    All methods to load data
    '''

    def get_info(self, i_query):
        self.update_query(i_query)
        return i_query.dump

    def get_data(self, query):
        self.update_query(query)
        image = self.find_tiles(query)
        return self.write_image(query, image)

    @staticmethod
    def make_data_query(i_query):
        # Begin building needed keywords
        i_path = i_query.OUTPUT.INFO.PATH

        return DataQuery(**{
            i_query.INPUT.METHODS.NAME: 'data',
            i_path.NAME: i_path.VALUE
        })

    @staticmethod
    def make_tile_query(query, t_index):
        tile_crop = query.all_in_some(t_index)
        return TileQuery(query, t_index, tile_crop)

    def update_query(self, query):
        keywords = self._cache.get(query.key)
        if not len(keywords):
            d_query = query
            # Create a preporatory data_query
            if not isinstance(query, DataQuery):
                d_query = self.make_data_query(query)
            # Create a preporatory tile_query
            t0_index = np.uint32([0,0,0])
            t0_query = self.make_tile_query(d_query, t0_index)
            # Update keywords and set the cache
            keywords = t0_query.preload_source
            self._cache.set(query.key, keywords)
        # Update current query with preloaded terms
        query.update_source(keywords)

    '''
    Image Specific Methods
    '''

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


    def load_tile(self, query, t_query):
        # grab request size for query
        t_bounds = t_query.target_bounds
        t_origin = t_query.tile_origin
        (K0,J0,I0),(K1,J1,I1) = t_bounds-t_origin

        # Load from cache or from disk if needed
        cache_tile = self._cache.get(t_query.key)
        if len(cache_tile):
            return cache_tile[K0:K1,J0:J1,I0:I1]
        # Load from disk
        tile = t_query.tile

        self._cache.set(t_query.key, tile)

        return tile[K0:K1,J0:J1,I0:I1]

    @staticmethod
    def view_volume(view, vol):
        # Set up a colormap
        def id_to_color(vol):
            colors = np.zeros((3,)+vol.shape).astype(np.uint8)
            colors[0] = np.mod(107*vol,700).astype(np.uint8)
            colors[1] = np.mod(509*vol,900).astype(np.uint8)
            colors[2] = np.mod(200*vol,777).astype(np.uint8)
            return np.moveaxis(colors,0,-1)

        # Colormap if a colormap view
        if view.VALUE == view.COLOR.NAME:
            return id_to_color(vol)
        return vol

    def write_image(self, query, volume):

        img_format = query.INPUT.IMAGE.FORMAT
        img_view = query.INPUT.IMAGE.VIEW
        img_type = query.OUTPUT.INFO.TYPE

        # Only if grayscale view is set
        if img_view.VALUE == img_view.GRAY.NAME:
            # set the view based on the format
            is_big_int = img_type.VALUE in img_type.ID_LIST
            no_big_int_gray = img_format.VALUE in img_format.COLOR_LIST
            # If big integers must not be grayscale, try colormap
            if is_big_int and no_big_int_gray:
                img_view.VALUE = img_view.COLOR.NAME

        # Use colormap / RGB style encoding of ID data
        vol = self.view_volume(img_view, volume)

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
