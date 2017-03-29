from Query import Query
import numpy as np

class DataQuery(Query):
    """ Describe ``INPUT.METHODS.IMAGE_LIST`` requests

    Arguments
    -----------
    args: list
        unused
    keywords: dict
        * `OUTPUT.INFO.PATH` (str) --
            the path to the given :class:`Datasource`
        * `INPUT.POSITION.Z` (int) --
            the full resolution z start of the image request
        * `INPUT.POSITION.Y` (int) --
            the full resolution y start of the image request
        * `INPUT.POSITION.X` (int) --
            the full resolution x start of the image request
        * `INPUT.POSITION.DEPTH` (int) --
            the requested scaled depth of the image request
        * `INPUT.POSITION.HEIGHT` (int) --
            the requested scaled height of the image request
        * `INPUT.POSITION.WIDTH` (int) --
            the requested scaled width of the image request
        * `INPUT.RESOLUTION.XY` (int) --
            the number of halvings along the X and Y axes
        * `INPUT.RESOLUTION.FORMAT` (str) --
            the requested output image file format
        * `INPUT.RESOLUTION.VIEW` (str) --
            the requested coloring method for images

    """

    #: default mime type for HTTP response
    _basic_mime = 'image/{}'

    def __init__(self,*args,**keywords):
        Query.__init__(self, **keywords)

        for key in ['Z','Y','X']:
            self.set_key(self.INPUT.POSITION, key, 0)

        for key in ['DEPTH','HEIGHT','WIDTH']:
            self.set_key(self.INPUT.POSITION, key, 1)

        for key in ['VIEW','FORMAT']:
            self.set_key(self.INPUT.IMAGE, key)

        self.set_key(self.OUTPUT.INFO, 'PATH')
        self.set_key(self.INPUT.RESOLUTION, 'XY', 0)

    @property
    def key(self):
        """ return the key for the database

        Returns
        -------
        str
            the path value from ``OUTPUT.INFO``
        """
        return self.OUTPUT.INFO.PATH.VALUE

    @property
    def dtype(self):
        """ return actual numpy dtype object

        Returns
        -------
        numpy.dtype
            from the type value from ``OUTPUT.INFO``
        """
        dtype = self.OUTPUT.INFO.TYPE.VALUE
        return getattr(np,dtype, np.uint8)

    @property
    def scales(self):
        """ convert a number of halvings to a scale array

        Returns
        -------
        numpy.ndarray
            A 3x1 array of the target/source voxel ratios
        """
        s_xy = 2 ** self.INPUT.RESOLUTION.XY.VALUE
        return np.float32([1,s_xy,s_xy])

    @property
    def blocksize(self):
        """ get the size of each :class:`Datasource` tile

        Returns
        -------
        numpy.ndarray
            The 3x1 block value from ``RUNTIME.IMAGE``
        """
        return np.uint32(self.RUNTIME.IMAGE.BLOCK.VALUE)

    @property
    def target_shape(self):
        """ Scaled target size of the requested volume

        Returns
        -------
        numpy.ndarray
            The 3x1 block of DEPTH, HEIGHT, WIDTH \
values from `INPUT.POSITION`
        """
        shapes = ['DEPTH','HEIGHT','WIDTH']
        dhw = map(self.INPUT.POSITION.get, shapes)
        return np.uint32([s.VALUE for s in dhw])

    @property
    def source_shape(self):
        """ Full source size of the requested volume

        Returns
        --------
        numpy.ndarray
            The 3x1 :meth:`target_shape` multiplied by \
the voxel scales from :meth:`scales`.
        """
        return np.uint32(self.target_shape * self.scales)

    @property
    def target_origin(self):
        """ Scaled target offset of the requested origin

        Returns
        --------
        numpy.ndarray
            The 3x1 block of Z, Y, and X in `INPUT.POSITION`
        """
        zyx = map(self.INPUT.POSITION.get,'ZYX')
        return np.uint32([c.VALUE for c in zyx])

    @property
    def source_origin(self):
        """ Full source offset of the requested origin

        Returns
        --------
        numpy.ndarray
            The 3x1 :meth:`target_origin` multiplied by \
the voxel scales from :meth:`scales`.
        """
        return np.uint32(self.target_origin * self.scales)

    @property
    def target_bounds(self):
        """ Scaled bounding box of the requested volume

        Returns
        --------
        numpy.ndarray
            The 2x3 joining of :meth:`target_origin` \
and :meth:`target_shape` transposed such that \
each row gives one of two bounding corners.
        """
        z0y0x0 = self.target_origin
        z1y1x1 = z0y0x0 + self.target_shape
        return np.c_[z0y0x0, z1y1x1].T

    @property
    def tile_bounds(self):
        """ Bounding box given by counting whole tiles

        Returns
        --------
        numpy.ndarray
            The 2x3 joining of the lowermost tile \
and the uppermost tile transposed such that \
a row gives the upper or lower limit of tiles.
        """
        target_bounds = self.target_bounds
        float_block = np.float32(self.blocksize)
        float_bounds = target_bounds / float_block
        # Find lowest tile index and highest tile index
        bounds_start = np.uint32(np.floor(float_bounds[0]))
        bounds_end = np.uint32(np.ceil(float_bounds[1]))
        return np.c_[bounds_start, bounds_end].T

    @property
    def tile_shape(self):
        """ The ranges of tiles needed for the request

        Returns
        --------
        numpy.ndarray
            The 3x1 difference of :meth:`tile_bounds` \
to give three numbers that count the number \
of tiles needed in all three directions.
        """
        return np.diff(self.tile_bounds,axis=0)[0]

    def some_in_all(self, t_origin, t_shape):
        """ The target subvolume needed by a given tile

        Arguments
        ----------
        t_origin: numpy.ndarray
            The 3x1 origin of the tile in the scaled \
target image
        t_shape: numpy.ndarray
            The 3x1 shape of the tile in the scaled \
target image

        Returns
        --------
        numpy.ndarray
            The 2x3 joining of ``t_origin`` and ``t_shape`` \
offset from :meth:`target_origin` and clipped by \
:meth:`target_shape` such that either row gives \
the upper or lower corner of the tile in the full \
scaled target volume.
        """

        tile_bounds = t_origin + np.outer([0,1],t_shape)
        some_in = tile_bounds - self.target_origin
        return np.clip(some_in, 0, self.target_shape)

    def all_in_some(self, t_index):
        """ The tile region inside the scaled target volume

        Arguments
        ----------
        t_index: numpy.ndarray
            The 3x1 tile offset of a tile from the origin

        Returns
        --------
        numpy.ndarray
            The 2x3 offset of :meth:`target_bounds` from \
the origin of ``tile_origin`` repetitions of \
:meth:`blocksize` such that either row gives \
an upper or lower corner of the total target \
volume within the requested ``t_index`` tile.
        """
        tile_origin = self.blocksize * t_index
        all_in = self.target_bounds - tile_origin
        return np.clip(all_in, 0, self.blocksize)

