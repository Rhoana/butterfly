from Datasource import Datasource
import tifffile as tiff
import numpy as np
import json
import cv2
import os

class BossGrid(Datasource):
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
        numpy.ndarray
            1/H/W image volume
        """
        # call superclass
        Datasource.load_tile(t_query)
        # Get needed field from t_query
        boss_field = t_query.RUNTIME.IMAGE.SOURCE.BOSS
        # Get parameters from t_query
        path_dict = boss_field.PATHS.VALUE
        i_z, i_y, i_x = t_query.index_zyx
        # Attempt to get path from dictionary
        z_path = path_dict.get(i_z,{})
        if type(z_path) is dict: 
            # Get path from dictionary
            path = z_path.get(i_y,{}).get(i_x,'')
        else:
            # Get path from string
            path = z_path.format(column=i_y, row=i_x)

        # Sanity check returns empty tile
        if not len(path) or not os.path.exists(path):
            return []

        # Read the image from the file
        return BossGrid.imread(path)[np.newaxis]

    @staticmethod
    def preload_source(t_query):
        """load info from example tile (image)

        Then gets three needed values from the given \
path from the :class:`TileQuery` t_query

        Arguments
        -----------
        t_query: :class:`TileQuery`
            Only the file path is needed

        Returns
        --------
        dict
            Will be empty if filename does not give \
a valid json file pointing to the tiff grid.

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
        boss_field = runtime.SOURCE.BOSS
        info_field = boss_field.INFO
        block_field = info_field.BLOCK
        full_field = info_field.EXTENT

        # Get the name and ending of the target file
        filename = t_query.OUTPUT.INFO.PATH.VALUE
        ending = os.path.splitext(filename)[1]

        # Return if the ending is not json
        if ending not in BossGrid._meta_files:
            return {}

        # Return if the path does not exist
        if not os.path.exists(filename):
            return {}

        # Get function to read the metainfo file
        order = BossGrid._meta_files.index(ending)
        reader = BossGrid._read[order]

        # Get information from json file
        with open(filename, 'r') as jd:
            # Get all the filenames
            all_info = readed(jd)
            boss = all_info.get(boss_field.ALL, [])
            info = all_info.get(info_field.NAME, {})
            # Return if no metadata
            if not len(info):
                return {}
            # For all the paths
            path_dict = {}

            # Read all paths in dictionary
            for d in boss: 
                path = d.get(boss_field.PATH, '')
                # Update the maximum value
                z,y,x = map(d.get, boss_field.ZYX)
                # Allow for simple section formats
                if not all([y,x]):
                    path_dict[z] = path
                    continue
                # Add section to the dictionary
                if z not in path_dict:
                    path_dict[z] = {
                        y: {
                            x: path
                        }
                    }
                    continue
                # Add column to dictionary
                if y not in path_dict[z]:
                    path_dict[z][y] = {
                        x: path
                    }
                    continue
                # Add row to dictionary
                path_dict[z][y][x] = path
            # Return if no paths
            if not len(path_dict):
                return {}

            # Shape of one tile
            block_info = info.get(block_field.NAME, {})
            block_list = map(block_info.get, block_field.ZYX)
            # Return if no block shape
            if not all(block_list):
                return {}

            # Shape of full volume
            full_info = info.get(full_field.NAME)
            full_extent = map(full_info.get, full_field.ZYX)
            # Return if no full extent shape
            if not all(full_extent):
                return {}

            # Block shape as a numpy array
            block_shape = np.uint64(block_list)
            if block_shape.shape != (3,):
                return {}
            # Finally, list all the mip levels
            block_shapes = block_shape[np.newaxis]

            # Full shape as a numpy array
            full_bounds = np.uint64(full_extent)
            if full_bounds.shape != (3,2):
                return {}
            # Finally, get the full shape from extent
            full_shape = np.diff(full_bounds)

            # All keys to follow API
            keywords = {
                runtime.BLOCK.NAME: block_shape[np.newaxis],
                output.SIZE.NAME: full_shape,
                output.TYPE.NAME: str(any_tile.dtype),
                boss_field.PATHS.NAME: path_dict,
            }

            # Combine results with parent method
            common = Datasource.preload_source(t_query)
            return dict(common, **keywords)

    @staticmethod
    def imread(_path):
        """ allow loading grayscale pngs as well as tiffs
        """
        if os.path.splitext(_path)[1] in ['.tiff', '.tif']:
            return tiff.imread(_path)
        else:
            return cv2.imread(_path,0)

