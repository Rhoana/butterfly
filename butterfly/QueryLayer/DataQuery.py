from Query import Query
import numpy as np
import logging

class DataQuery(Query):

    def __init__(self,*args,**keywords):
        Query.__init__(self, **keywords)

        for key in ['X','Y','Z','WIDTH','HEIGHT']:
            self.set_key(self.INPUT.POSITION,key)

        for key in ['VIEW','FORMAT']:
            self.set_key(self.INPUT.IMAGE,key)

        for key in ['SOURCE','BLOCK']:
            self.set_key(self.RUNTIME.IMAGE, key)

        for key in ['TYPE','PATH']:
            self.set_key(self.OUTPUT.INFO, key)

        self.set_key(self.INPUT.RESOLUTION, 'XY')

    @property
    def key(self):
        return self.OUTPUT.INFO.PATH.VALUE

    @property
    def dtype(self):
        dtype = self.OUTPUT.INFO.TYPE.VALUE
        return getattr(np,dtype, np.uint8)

    @property
    def content_type(self):
        img_format = self.INPUT.IMAGE.FORMAT
        is_img = img_format.VALUE not in img_format.ZIP_LIST
        content_type = self.content_types[is_img]
        return content_type.replace('{fmt}', img_format.VALUE)

    @property
    def scale(self):
        return np.float32(2 ** self.INPUT.RESOLUTION.XY.VALUE)

    @property
    def blocksize(self):
        return np.uint32(self.RUNTIME.IMAGE.BLOCK.VALUE)

    @property
    def target_shape(self):
        get_val = lambda k: getattr(self.INPUT.POSITION,k).VALUE
        return np.uint32(map(get_val,['DEPTH','HEIGHT','WIDTH']))

    @property
    def source_shape(self):
        return np.uint32(self.target_shape * self.scale)

    @property
    def target_origin(self):
        return np.uint32(self.source_origin / self.scale)

    @property
    def source_origin(self):
        get_val = lambda k: getattr(self.INPUT.POSITION,k).VALUE
        return np.uint32(map(get_val,'ZYX'))

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

    def tile2target(self, tile_index):
        tile_start = self.blocksize * tile_index
        tile_end = self.blocksize * (tile_index+1)
        return np.c_[tile_start, tile_end].T

    def some_in_all(self, t_index, t_shape, offset):
        tile_origin = self.blocksize * t_index
        target_origin = self.target_origin
        some_origin = tile_origin + offset
        start = some_origin - target_origin
        return np.c_[start, start + t_shape].T

    def all_in_some(self, t_index):
        origin = self.blocksize * t_index
        all_in = self.target_bounds - origin
        return np.clip(all_in, 0, self.blocksize)

