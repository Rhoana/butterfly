from Datasource import Datasource

class TileSpecs(Datasource):
    """ Not implemented
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
            * :data:`OUTPUT.INFO`.``TYPE.NAME`` -- \ 
                numpy datatype of any given tile
            * :data:`RUNTIME.IMAGE`.``BLOCK.NAME`` -- \ 
                numpy 3x1 array of any given tile shape
            * :data:`OUTPUT.INFO`.``SIZE.NAME`` -- \ 
                numpy 3x1 array of full volume shape
        """
        return {}
