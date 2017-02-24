from Query import Query
import numpy as np
import logging

class DataQuery(Query):

    def __init__(self,*args,**keywords):
        Query.__init__(self, **keywords)

        positions = ['X','Y','Z','WIDTH','HEIGHT']
        for key in positions:
            self.set_key(self.INPUT.POSITION,key)

        image_list = ['VIEW','FORMAT']
        for key in image_list:
            self.set_key(self.INPUT.IMAGE,key)

        self.OUTPUT.INFO.TYPE.VALUE = 'uint8'
        self.RUNTIME.IMAGE.SOURCE.VALUE = 'hdf5'
        self.RUNTIME.IMAGE.BLOCK.VALUE = [512,512]
        self.set_key(self.INPUT.RESOLUTION,'XY')
        self.set_key(self.OUTPUT.INFO,'PATH')

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
        return np.uint32(map(get_val,['HEIGHT','WIDTH']))

    @property
    def source_shape(self):
        return np.uint32(self.target_shape * self.scale)

    @property
    def target_origin(self):
        return np.uint32(self.source_origin / self.scale)

    @property
    def source_origin(self):
        get_val = lambda k: getattr(self.INPUT.POSITION,k).VALUE
        return np.uint32(map(get_val,'YX'))

    @property
    def target_bounds(self):
        y0x0 = self.target_origin
        y1x1 = y0x0 + self.target_shape
        return [y0x0, y1x1]

    @property
    def tile_bounds(self):
        target_bounds = self.target_bounds
        float_block = np.float32(self.blocksize)
        start = target_bounds[0] / float_block
        end = target_bounds[1] / float_block

        bounds_start = np.floor(start).astype(np.uint32)
        bounds_end = np.ceil(end).astype(np.uint32)
        return [bounds_start, bounds_end]

    @property
    def tile_shape(self):
        return -np.subtract(*self.tile_bounds)

    def tile2target(self, tile_index):
        tile_start = self.blocksize * tile_index
        tile_end = self.blocksize * (tile_index+1)
        return [tile_start, tile_end]

    def some_in_all(self, t_index, t_shape):
        target_origin = self.target_bounds[0]
        tile_origin = self.tile2target(t_index)[0]
        start = tile_origin - target_origin
        return [start, start+t_shape[1:]]

    def all_in_some(self, t_index):
        some_shape = self.blocksize
        all_in = self.target_bounds
        origin = self.tile2target(t_index)[0]
        clip_off = lambda i: np.clip(i-origin,0,some_shape)
        return [t_index] + map(clip_off, all_in)

