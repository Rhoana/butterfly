from AccessLayer.QueryLayer import TileQuery
from AccessLayer.QueryLayer import DataQuery
from Cache import Cache
import numpy as np
import tifffile
import StringIO
import zlib
import cv2

class Core(object):
    """ Starts the :class:`Cache`

    Arguments
    -----------
    db : :data:`bfly.Butterfly._db_type`
        A fully-loaded database

    Attributes
    ------------
    _db: :data:`bfly.Butterfly._db_type`
        Taken from first argument ``db``
    _cache: :class:`Cache`
        Able to store images and metadata using \ 
        :class:`UtilityLayer.RUNTIME` instance \ 
        from ``db`` argument
    """
    def __init__(self, db):
        # Get DB Terms
        self._db = db
        RUNTIME = db.RUNTIME

        # Make Cache with keywords
        self._cache = Cache(RUNTIME)

    #####
    # All methods to load data
    #     1. get_info answers an InfoQuery i_query. 
    #     2. get_data answers a DataQuery d_query.
    #
    # Both get_info or get_data call update_query.
    #
    # To give answers , update_query uses _cache or:
    #     1. make_data_query if only i_query given.
    #     2. make_tile_query with new or given d_query.
    #####

    def get_info(self, i_query):
        """ dumps answer to ``i_query`` as a string

        Calls :meth:`update_query` with more information\ 
        from the cache or from the properties of a tile.

        Arguments
        ----------
        i_query: :class:`QueryLayer.InfoQuery`
            A request for information

        Returns
        --------
        str
            Answer for the :class:`QueryLayer.InfoQuery`
        """
        self.update_query(i_query)
        return i_query.dump

    def get_data(self, d_query):
        """ dumps answer to ``d_query`` as a string

        Calls :meth:`update_query` with more information\ 
        from the cache or from the properties of a tile. \ 
        Also calls :meth:`find_tiles` to get the complete\ 
        image needed to answer the ``d_query``.

        Arguments
        ----------
        i_query: :class:`QueryLayer.InfoQuery`
            A request for information

        Returns
        --------
        str
            Answer for the :class:`QueryLayer.InfoQuery`
        """

        self.update_query(d_query)
        image = self.find_tiles(d_query)
        return self.write_image(d_query, image)

    @staticmethod
    def make_data_query(i_query):
        """ Make a data query from an info query

        Arguments
        ----------
        i_query: :class:`InfoQuery`
            only needs ``PATH`` set in :data:`OUTPUT.INFO`

        Returns
        --------
        :class:`DataQuery`
            takes only the `PATH` from ``i_query``

        """
        # Begin building needed keywords
        i_path = i_query.OUTPUT.INFO.PATH

        return DataQuery(**{
            i_query.INPUT.METHODS.NAME: 'data',
            i_path.NAME: i_path.VALUE
        })

    @staticmethod
    def make_tile_query(d_query, t_index):
        """ Make a :class:`TileQuery` from :class:`DataQuery`

        Arguments
        ----------
        d_query: :class:`DataQuery`
            only needs ``PATH`` set in :data:`OUTPUT.INFO`
        t_index: numpy.ndarray
            The 3x1 count of tiles form the origin

        Returns
        --------
        :class:`TileQuery`
            One tile request in the given data request
        """
        tile_crop = d_query.all_in_some(t_index)
        return TileQuery(d_query, t_index, tile_crop)

    def update_query(self, query):
        """ Finds missing query details from cache or tile

        Calls :meth:`Query.update_source` with ``keywords`` \ 
        taken from either the :data:`_cache` or from a new \ 
        :class:`TileQuery` to update the given ``query``

        Arguments
        ----------
        query: :class:`Query`
            Either an :class:`InfoQuery` or a :class:`DataQuery`
        """
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

    #####
    # Image Specific Methods
    #####

    def find_tiles(self, d_query):
        """ Load the requested image for a :class:`DataQuery`

        Arguments
        ----------
        d_query: :class:`DataQuery`
            Request for a scaled subvolume of a source image

        Returns
        numpy.ndarray
            The full image data for the requested region
        """
        first_tile_index = d_query.tile_bounds[0]
        all_tiles = np.argwhere(np.ones(d_query.tile_shape))
        cutout = np.zeros(d_query.target_shape, d_query.dtype)
        tiles_needed = first_tile_index + all_tiles

        for t_index in tiles_needed:
            # Make a query for the given tile
            t_query = self.make_tile_query(d_query, t_index)
            tile = self.load_tile(t_query)
            # Fill the tile into the full cutout
            to_cut = [t_query.target_origin, tile.shape]
            [Z0,Y0,X0],[Z1,Y1,X1] = d_query.some_in_all(*to_cut)
            cutout[Z0:Z1,Y0:Y1,X0:X1] = tile

        return cutout

    def load_tile(self, t_query):
        """ Load a single tile from the cache or from disk

        Arguments
        ----------
        t_query: :class:`TileQuery`
            With tile coordinates and volume within the tile

        Returns
        --------
        numpy.ndarray
            The subregion image data for the requested tile
        """
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
        """ Display a volume in color or grayscale

        Arguments
        ----------
        view: str
            The requested color or gray view of the data
        vol: str
            Raw volume from :class:`Cache` / :class:`Datasource`

        Returns
        --------
        numpy.ndarray
            Colorized or original raw volume
        """
        # Set up a colormap
        def id_to_color(vol):
            colors = np.zeros((3,)+ vol.shape).astype(np.uint8)
            colors[0] = np.mod(107 * vol, 700).astype(np.uint8)
            colors[1] = np.mod(509 * vol, 900).astype(np.uint8)
            colors[2] = np.mod(200 * vol, 777).astype(np.uint8)
            return np.moveaxis(colors,0,-1)

        # Colormap if a colormap view
        if view.VALUE == view.COLOR.NAME:
            return id_to_color(vol)
        return vol

    def write_image(self, d_query, volume):
        """ Format a volume for a given :class:`DataQuery`

        Arguments
        ----------
        d_query: :class:`DataQuery`
            With the format and view for the requested volume
        volume: numpy.ndarray
            Raw volume from :class:`Cache` / :class:`Datasource`

        Returns
        --------
        str:
            The image response as a formatted bytestring
        """
        img_format = d_query.INPUT.IMAGE.FORMAT
        img_view = d_query.INPUT.IMAGE.VIEW
        img_type = d_query.OUTPUT.INFO.TYPE

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
