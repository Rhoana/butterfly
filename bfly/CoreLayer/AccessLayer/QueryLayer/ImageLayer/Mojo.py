from Datasource import Datasource

class Mojo(Datasource):
    """ Not implemented
    """
    @staticmethod
    def load_tile(t_query):
        """load a single tile (image)

        Arguments
        -----------
        t_query: :class:`TileQuery`
            With file path and image position

        Returns
        -----------
        np.ndarray
            An image array that may be as large \
as an entire full resolution slice of \
the whole hdf5 volume. Based on the value \
of :meth:`TileQuery.all_scales`, this array \
will likely be downsampled by to a small fraction \
of the full tile resolution.
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
            Will be empty if filename does not give \
a valid mojo directory.

            * :class:`RUNTIME` ``.IMAGE.BLOCK.NAME``
                (numpy.ndarray) -- 3x1 for any give tile shape
            * :class:`OUTPUT` ``.INFO.TYPE.NAME``
                (str) -- numpy dtype of any given tile
            * :class:`OUTPUT` ``.INFO.SIZE.NAME``
                (numpy.ndarray) -- 3x1 for full volume shape
        """
        return {}
