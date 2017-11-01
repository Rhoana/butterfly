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
        path = path_dict.get(i_z,{}).get(i_y,{}).get(i_x,'')

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
            boss = reader(jd).get(boss_field.ALL, [])
            # Get all the paths
            path_dict = {}
            # Get the max offset
            max_zyx = np.uint32([0,0,0])

            # Read all paths in dictionary
            for d in boss: 
                path = d.get(boss_field.PATH, '')
                # Update the maximum value
                z,y,x = map(d.get, boss_field.ZYX)
                max_zyx = np.maximum(max_zyx, [z,y,x])
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
            if not np.any(max_zyx):
                return {}
            # Index of edge of volume
            index_size = max_zyx + 1

            # Get arbitrary path from dictionary
            any_v = lambda d: d[next(iter(d))]
            any_path = any_v(any_v(any_v(path_dict)))
            # Get the tile size from a tile
            any_tile = BossGrid.imread(any_path)
            tile_shape = np.uint32((1,) + any_tile.shape)

            # The size of the full volume
            full_shape = tile_shape * index_size

            # All keys to follow API
            keywords = {
                runtime.BLOCK.NAME: tile_shape[np.newaxis],
                output.SIZE.NAME: np.uint32(full_shape),
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

