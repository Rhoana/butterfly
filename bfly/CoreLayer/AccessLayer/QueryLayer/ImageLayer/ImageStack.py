from Datasource import Datasource
import tifffile as tiff
import numpy as np
import glob
import json
import cv2
import os

class ImageStack(Datasource):
    @staticmethod
    def load_tile(t_query):
        """load a single tile (image)

        Arguments
        -----------
        t_query: :class:`TileQuery`
            With file path and image position
        """
        # read all tifs in tifs folder
        search = os.path.join(t_query.path, '*')
        stack = sorted(glob.glob(search))

        # Read tif at current z 
        i_z = t_query.index_zyx[0]
        filepath = stack[i_z]
        return ImageStack.imread(filepath)[np.newaxis]

    @staticmethod
    def preload_source(t_query):
        """load info from example tile (image)

        Arguments
        -----------
        t_query: :class:`TileQuery`
            Only the file path is needed

        Returns
        --------
        dict
            * :data:`OUTPUT.INFO`.``TYPE.NAME`` -- \
numpy datatype of any given tile
            * :data:`RUNTIME.IMAGE`.``BLOCK.NAME`` -- \
numpy 3x1 array of any given tile shape
            * :data:`OUTPUT.INFO`.``SIZE.NAME`` -- \
numpy 3x1 array of full volume shape
        """
        # read all tifs in tifs folder
        search = os.path.join(t_query.path, '*')
        depth = len(list(glob.glob(search)))
        # Should count files on filesystem
        N_FILES = np.uint32([depth, 1, 1])
        tile_0 = ImageStack.load_tile(t_query)
        # Return empty if can't load first tile
        if not len(tile_0):
            return {}
        # Get properties from example tile
        FILE_SIZE = tile_0.shape
        FULL_SIZE = FILE_SIZE * N_FILES
        DATA_TYPE = str(tile_0.dtype)

        # 'block-size', 'dimensions', and 'data-type'
        k_block = t_query.RUNTIME.IMAGE.BLOCK.NAME
        k_size = t_query.OUTPUT.INFO.SIZE.NAME
        k_type = t_query.OUTPUT.INFO.TYPE.NAME
        
        # Combine results with parent method
        common = Datasource.preload_source(t_query)
        return dict(common, **{
            k_block: np.uint32([FILE_SIZE]),
            k_size: np.uint32(FULL_SIZE),
            k_type: DATA_TYPE,
        })

    @staticmethod
    def imread(_path):
        """ allow loading grayscale pngs as well as tiffs
        """
        if os.path.splitext(_path)[1] in ['.tiff', '.tif']:
            return tiff.imread(_path)
        else:
            return cv2.imread(_path,0)

