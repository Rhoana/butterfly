from Query import Query
import numpy as np

class DataQuery(Query):

    basic_mime = 'image/{}'

    def __init__(self,*args,**keywords):
        Query.__init__(self, **keywords)

        for key in ['Z','Y','X']:
            self.set_key(self.INPUT.POSITION,key,0)

        for key in ['DEPTH','HEIGHT','WIDTH']:
            self.set_key(self.INPUT.POSITION,key,1)

        for key in ['VIEW','FORMAT']:
            self.set_key(self.INPUT.IMAGE,key)

        self.set_key(self.OUTPUT.INFO, 'PATH')
        self.set_key(self.INPUT.RESOLUTION, 'XY', 0)

    @property
    def key(self):
        return self.OUTPUT.INFO.PATH.VALUE

    @property
    def dtype(self):
        dtype = self.OUTPUT.INFO.TYPE.VALUE
        return getattr(np,dtype, np.uint8)

    @property
    def scales(self):
        s_xy = 2 ** self.INPUT.RESOLUTION.XY.VALUE
        return np.float32([1,s_xy,s_xy])

    @property
    def blocksize(self):
        return np.uint32(self.RUNTIME.IMAGE.BLOCK.VALUE)

    @property
    def target_shape(self):
        shapes = ['DEPTH','HEIGHT','WIDTH']
        dhw = map(self.INPUT.POSITION.get, shapes)
        return np.uint32([s.VALUE for s in dhw])

    @property
    def source_shape(self):
        return np.uint32(self.target_shape * self.scales)

    @property
    def target_origin(self):
        return np.uint32(self.source_origin / self.scales)

    @property
    def source_origin(self):
        zyx = map(self.INPUT.POSITION.get,'ZYX')
        return np.uint32([c.VALUE for c in zyx])

    @property
    def target_bounds(self):
        z0y0x0 = self.target_origin
        z1y1x1 = z0y0x0 + self.target_shape
        return np.c_[z0y0x0, z1y1x1].T

    @property
    def tile_bounds(self):
        target_bounds = self.target_bounds
        float_block = np.float32(self.blocksize)
        float_bounds = target_bounds / float_block
        # Find lowest tile index and highest tile index
        bounds_start = np.uint32(np.floor(float_bounds[0]))
        bounds_end = np.uint32(np.ceil(float_bounds[1]))
        return np.c_[bounds_start, bounds_end].T

    @property
    def tile_shape(self):
        return np.diff(self.tile_bounds,axis=0)[0]

    def some_in_all(self, t_origin, t_shape):
        tile_bounds = t_origin + np.outer([0,1],t_shape)
        some_in = tile_bounds - self.target_origin
        return np.clip(some_in, 0, self.target_shape)

    def all_in_some(self, t_index):
        tile_origin = self.blocksize * t_index
        all_in = self.target_bounds - tile_origin
        return np.clip(all_in, 0, self.blocksize)

