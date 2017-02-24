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
    def is_zip(self):
        fmt = self.INPUT.IMAGE.FORMAT.VALUE
        return fmt in self.INPUT.IMAGE.FORMAT.ZIP_LIST

    @property
    def dtype(self):
        dtype = self.OUTPUT.INFO.TYPE.VALUE
        return getattr(np,dtype,np.uint8)

    @property
    def content_type(self):
        is_img = not self.is_zip
        fmt = self.INPUT.IMAGE.FORMAT.VALUE
        content_type = self.content_types[is_img]
        return content_type.replace('{fmt}', fmt)

    @property
    def scale(self):
        return np.float32(2 ** self.INPUT.RESOLUTION.XY.VALUE)

    @property
    def blocksize(self):
        target_block = self.RUNTIME.IMAGE.BLOCK.VALUE
        return np.array(target_block, dtype=np.uint32)

    @property
    def target_shape(self):
        get_val = lambda k: getattr(self.INPUT.POSITION,k).VALUE
        return map(get_val,['HEIGHT','WIDTH'])

    @property
    def source_shape(self):
        upscale = lambda s: np.uint32(s * self.scale)
        return map(upscale, self.target_shape)

    @property
    def target_origin(self):
        downscale = lambda s: np.uint32(s / self.scale)
        return map(downscale, self.source_origin)

    @property
    def source_origin(self):
        get_val = lambda k: getattr(self.INPUT.POSITION,k).VALUE
        return map(get_val,'YX')

    @property
    def target_bounds(self):
        y0x0 = np.array(self.target_origin)
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

    def some_in_all(self, t_index):
        all_shape = self.target_shape
        origin = self.target_bounds[0]
        some_in = self.tile2target(t_index)
        clip_off = lambda i: np.clip(i-origin,0,all_shape)
        return map(clip_off, some_in)

    def all_in_some(self, t_index):
        some_shape = self.blocksize
        all_in = self.target_bounds
        origin = self.tile2target(t_index)[0]
        clip_off = lambda i: np.clip(i-origin,0,some_shape)
        return map(clip_off, all_in)

