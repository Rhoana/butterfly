from ImageLayer import HDF5
from ImageLayer import Mojo
from ImageLayer import TiffGrid
from urllib2 import URLError
from Query import Query
import numpy as np
import sys
import os

class TileQuery(Query):
    """ Describe requsts for tiles from a :class:`Datasource`

    Arguments
    ----------
    args: list
        * (:class:`DataQuery`) gives the full volume request
        * (numpy.ndarray) 3x1 tile offset of the given tile
        * (numpy.ndarray) 2x3 subregion within given tile
    keywords: dict
        unused

    Attributes
    -----------
    source_list: list
        from :class:`RUNTIME` ``.IMAGE.SOURCE.LIST``
    SOURCES: dict
        * source_list[0]: :class:`HDF5`
        * source_list[1]: :class:`TiffGrid`
    """
    def __init__(self, *args, **keywords):

        Query.__init__(self, **keywords)

        query, zyx_index, kji_pixels = args
        self.source_list = self.RUNTIME.IMAGE.SOURCE.LIST

        self.SOURCES = {
            self.source_list[0]: HDF5,
            self.source_list[1]: TiffGrid,
            self.source_list[2]: Mojo,
        }

        self.RUNTIME.TILE.ZYX.VALUE = zyx_index
        self.RUNTIME.TILE.KJI.VALUE = kji_pixels
        self.RUNTIME.TILE.SCALES.VALUE = query.scales

        # Set blocksize from the query
        self.blocksize = query.blocksize

        # Get the right blocksize, datatype, and path
        q_type = query.OUTPUT.INFO.TYPE.VALUE
        q_path = query.OUTPUT.INFO.PATH.VALUE

        # Set the right blocksize, datatype, and path
        self.OUTPUT.INFO.TYPE.VALUE = q_type
        self.OUTPUT.INFO.PATH.VALUE = q_path

        # Very important to get the right datasource
        query_source = query.RUNTIME.IMAGE.SOURCE
        self_source = self.RUNTIME.IMAGE.SOURCE
        self_source.VALUE = query_source.VALUE

        # Only applies to HDF5 datasource
        query_h5 = query.RUNTIME.IMAGE.SOURCE.HDF5
        self_h5 = self.RUNTIME.IMAGE.SOURCE.HDF5
        self_h5.VALUE = query_h5.VALUE

        # Only applies to Mojo datasource
        query_format = query.RUNTIME.IMAGE.SOURCE.MOJO.FORMAT
        self_format = self.RUNTIME.IMAGE.SOURCE.MOJO.FORMAT
        self_format.VALUE = query_format.VALUE

        # Get the XY resolution for Mojo
        query_xy = query.INPUT.RESOLUTION.XY
        self_xy = self.INPUT.RESOLUTION.XY
        self_xy.VALUE = query_xy.VALUE

    @property
    def key(self):
        """ return the key for the database

        Returns
        -------
        str
            the path value from :meth:`path` \
joined with the tile_values from \
:meth:`index_zyx` and :meth:`all_scales`
        """
        origin = self.index_zyx
        scales = self.all_scales
        tile_values = np.r_[scales,origin]
        tile_key =  np.array2string(tile_values)
        return self.path + tile_key

    @property
    def tile(self):
        """ Load the requested tile from the source

        Returns
        --------
        numpy.ndarray
            The full image loaded by :meth:`my_source`
        """
        return self.my_source.load_tile(self)

    @property
    def path(self):
        """ return the path to the whole volume

        Returns
        -------
        str
            the path value from ``OUTPUT.INFO``
        """
        return self.OUTPUT.INFO.PATH.VALUE

    @property
    def my_source(self):
        """ return the source that loads this tile

        Returns
        -------
        :class:`Datasource`
            the source value from ``RUNTIME.IMAGE`` \
as an actual :class:`Datasource` \
that can load a ``TileQuery``.
        """
        my_source = self.RUNTIME.IMAGE.SOURCE.VALUE
        return self.get_source(my_source)

    @property
    def all_scales(self):
        """ A scale array from ``RUNTIME.TILE``

        Returns
        -------
        numpy.ndarray
            A 3x1 array of the target/source voxel ratios
        """
        return np.uint32(self.RUNTIME.TILE.SCALES.VALUE)

    @property
    def pixels_kji(self):
        """The pixels bounds needed from the tile

        Returns
        --------
        numpy.ndarray
            The 2x3 subregion within the given tile
        """
        return np.uint32(self.RUNTIME.TILE.KJI.VALUE)

    @property
    def index_zyx(self):
        """The tile offsets needed to get the tile

        Returns
        --------
        numpy.ndarray
            3x1 tile offset of the given tile
        """
        return np.uint32(self.RUNTIME.TILE.ZYX.VALUE)

    @property
    def target_tile_bounds(self):
        """The scaled target bounds of the tile

        Returns
        --------
        numpy.ndarray
            2x3 scaled target pixel bounds
        """
        # Get the target offset from the target origin
        tile_origin = self.index_zyx * self.blocksize
        offset = np.outer([0,1], self.blocksize)
        return tile_origin + offset

    @property
    def source_tile_bounds(self):
        """The full image bounds of the tile

        Returns
        --------
        numpy.ndarray
            2x3 full image pixel bounds
        """
        return self.all_scales * self.target_tile_bounds

    @property
    def target_origin(self):
        """The origin of query in target coordinates

        Returns
        --------
        numpy.ndarray
            3x1 target pixel lower bound
        """
        return  self.target_bounds[0]

    @property
    def target_bounds(self):
        """The bounds of query in target coordinates

        Returns
        --------
        numpy.ndarray
        2x3 target pixel boundaries
        """
        return self.pixels_kji + self.target_tile_bounds[0]

    @property
    def source_bounds(self):
        """The bounds of query in full coordinates

        Returns
        --------
        numpy.ndarray
            2x3 full source pixel bounds in tile
        """
        return self.all_scales * self.target_bounds

    @property
    def preload_source(self):
        """ Get a :meth:`valid_source` with a measured size

        Returns
        --------
        dict
            Empty if no :meth:`valid_source`

            * :class:`RUNTIME` ``.CACHE.META.NAME``
                (int) -- The byte size of this dictionary
            * :class:`RUNTIME` ``.IMAGE.SOURCE.NAME``
                (str) -- The :class:`Datasource` subclass
            * :class:`RUNTIME` ``.IMAGE.BLOCK.NAME``
                (numpy.ndarray) -- 3x1 for any give tile shape
            * :class:`OUTPUT` ``.INFO.TYPE.NAME``
                (str) -- numpy dtype of any given tile
            * :class:`OUTPUT` ``.INFO.SIZE.NAME``
                (numpy.ndarray) -- 3x1 for full volume shape
        """
        # Get all the metadata needed for the cache
        cache_meta = self.RUNTIME.CACHE.META
        # Preload the metadata from the source
        keywords = self.valid_source

        # Get the size of this dictionary for the cache
        dict_size = np.uint32(sys.getsizeof({}))
        keywords[cache_meta.NAME] = dict_size
        # calculate the size
        for key in keywords.keys():
            n_bytes = sys.getsizeof(keywords[key])
            keywords[cache_meta.NAME] += n_bytes
        # Return keywords for cache and dataQuery
        return keywords

    @property
    def valid_source(self):
        """ Call ``preload_source`` for all :data:`source_list`

        Returns
        --------
        dict
            Empty if no :meth:`Datasource.preload_source` \
can find this filname to give a valid volume.

            * :class:`RUNTIME` ``.IMAGE.SOURCE.NAME``
                (str) -- The :class:`Datasource` subclass
            * :class:`RUNTIME` ``.IMAGE.BLOCK.NAME``
                (numpy.ndarray) -- 3x1 for any give tile shape
            * :class:`OUTPUT` ``.INFO.TYPE.NAME``
                (str) -- numpy dtype of any given tile
            * :class:`OUTPUT` ``.INFO.SIZE.NAME``
                (numpy.ndarray) -- 3x1 for full volume shape
        """
        # Get the path key and value
        k_path = self.OUTPUT.INFO.PATH.NAME
        v_path = self.OUTPUT.INFO.PATH.VALUE
        # Make sure we have a valid pathname
        if not os.path.exists(v_path):
            msg = 'The {} {} does not exist on the server.'
            msg.format(k_path, v_path)
            raise URLError([msg, 503])
        # Get the default source
        my_source = self.RUNTIME.IMAGE.SOURCE
        # Validate the source of self.path
        for name in self.source_list:
            source = self.get_source(name)
            # Ask if source can load self path
            keywords = source.preload_source(self)
            if len(keywords):
                # Set valid source
                keywords[my_source.NAME] = name
                return keywords
        # return empty
        return {}

    def get_source(self, name):
        """ Gets a ``Datasource`` from :data:`SOURCES`

        Arguments
        ----------
        name: str
            The key to a ``Datasource`` subclass \
as listed in :data:`SOURCES`

        Returns
        --------
        :class:`Datasource`
            A ``Datasource`` subclass given by ``name``
        """
        return self.SOURCES.get(name, HDF5)
