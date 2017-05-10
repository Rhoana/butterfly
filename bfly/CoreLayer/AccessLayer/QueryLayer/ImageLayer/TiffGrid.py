from Datasource import Datasource
import tifffile as tiff
import numpy as np
import json
import cv2
import os

class TiffGrid(Datasource):
    """ Loads images from hdf5 files

    Attributes
    ------------
    _read: list
        All load functions for :data:`_meta_files`
    """

    # All readers for _meta_files
    _read = [json.load]
    #: All extensions of files pointing to h5
    _meta_files = ['.json']

    @staticmethod
    def load_tile(t_query):
        """load a single tile (image)

        Gets the image path from the \
:data:`TileQuery.RUNTIME`. ``IMAGE`` attribute.

        Gets the position of the image with the whole \
volume from :meth:`TileQuery.all_scales`, \
:meth:`TileQuery.tile_origin`, and \
:meth:`TileQuery.blocksize`.

        Arguments
        -----------
        t_query: :class:`TileQuery`
            With file path and image position

        Returns
        --------
        None
        """
        # call superclass
        Datasource.load_tile(t_query)

        return None

    @staticmethod
    def preload_source(t_query):
        """load info from example tile (image)

        Calls :meth:`valid_path` to get filename and \
inner dataset path for the full h5 image volume.

        Then gets three needed values from the given \
path from the :class:`TileQuery` t_query

        Arguments
        -----------
        t_query: :class:`TileQuery`
            Only the file path is needed

        Returns
        --------
        dict
            Will be empty if :meth:`valid_path` finds\
this filname to not give a valid h5 volume.

            * :class:`RUNTIME` ``.IMAGE.BLOCK.NAME``
                (numpy.ndarray) -- 3x1 for any give tile shape
            * :class:`OUTPUT` ``.INFO.TYPE.NAME``
                (str) -- numpy dtype of any given tile
            * :class:`OUTPUT` ``.INFO.SIZE.NAME``
                (numpy.ndarray) -- 3x1 for full volume shape
        """
        # Keyword names
        output = t_query.OUTPUT.INFO
        runtime = t_query.RUNTIME.IMAGE
        tiff_field = runtime.SOURCE.TIFF

        # Get the name and ending of the target file
        filename = t_query.OUTPUT.INFO.PATH.VALUE
        ending = os.path.splitext(filename)[1]

        # call superclass
        Datasource.preload_source(t_query)

        # Return if the ending is not json
        if ending not in TiffGrid._meta_files:
            return {}

        # Return if the path does not exist
        if not os.path.exists(filename):
            return {}

        # Get function to read the metainfo file
        order = TiffGrid._meta_files.index(ending)
        reader = TiffGrid._read[order]

        # Get information from json file
        with open(filename, 'r') as jd:
            # Get all the filenames
            all = reader(jd).get(tiff_field.ALL, [])
            # Get all the paths
            def get_path(d):
                return d.get(tiff_field.PATH, '')
            all_path = map(get_path, all)
            # Get all the offsets
            def get_offset(d):
                return map(d.get, tiff_field.ZYX)
            # Get the offsets and the max offset
            all_off = np.uint32(map(get_offset, all))
            index_size = np.amax(all_off, 0) + 1
            # Get the tile size from first tile
            tile0 = TiffGrid.imread(all_path[0])
            tile_shape = np.uint32((1,) + tile0.shape)
            # The size and datatype of the full volume
            full_shape = tile_shape * index_size

            return {
                runtime.BLOCK.NAME: tile_shape[np.newaxis],
                output.SIZE.NAME: np.uint32(full_shape),
                output.TYPE.NAME: str(tile0.dtype),
            }

    @staticmethod
    def imread(_path):
        """ allow loading grayscale pngs as well as tiffs
        """
        if os.path.splitext(_path)[1] in ['.tiff', '.tif']:
            return tiff.imread(_path)
        else:
            return cv2.imread(_path,0)

