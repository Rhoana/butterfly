import os
import Sparse
import numpy as np

class Datasource(object):
    """ Loads images from files on the server
    """
    @staticmethod
    def load_tile(t_query):
        """load a single tile (image)

        Arguments
        -----------
        t_query: :class:`TileQuery`
            With file path and image position
        """
        return None

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
            * :class:`RUNTIME` ``.IMAGE.BLOCK.NAME``
                (numpy.ndarray) -- 3x1 for any given tile shape
            * :class:`OUTPUT` ``.INFO.TYPE.NAME``
                (str) -- numpy dtype of any given tile
            * :class:`OUTPUT` ``.INFO.SIZE.NAME``
                (numpy.ndarray) -- 3x1 for full volume shape
            * :class:`OUTPUT` ``.IMAGE.MERGE.NAME``
                ([list]) -- All sets of merged ids
            * :class:`OUTPUT` ``.IMAGE.ERROR.NAME``
                dict -- All error messages
        """
        # take named keywords
        RUNTIME = t_query.RUNTIME
        k_merge = RUNTIME.IMAGE.MERGE.NAME
        k_error = RUNTIME.IMAGE.ERROR.NAME
        # Return merges and error message
        return {
            k_merge : Sparse.load(t_query.path)[0],
            k_error : '',
        }
