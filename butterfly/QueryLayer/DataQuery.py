from Query import Query
import numpy as np
import logging

class DataQuery(Query):

    groups = []

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

        for g in self.INPUT.GROUP.LIST:
            self.groups.append(keywords.get(g,''))

    @property
    def key(self):
        return '_'.join(self.groups)

    @property
    def is_zip(self):
        fmt = self.INPUT.IMAGE.FORMAT.VALUE
        return fmt in self.INPUT.IMAGE.FORMAT.ZIP_LIST

    @property
    def content_type(self):
        is_img = not self.is_zip
        fmt = self.INPUT.IMAGE.FORMAT.VALUE
        content_type = self.content_types[is_img]
        return content_type.replace('{fmt}', fmt)

    @property
    def blocksize(self):
        blocksize = self.RUNTIME.IMAGE.BLOCK.VALUE
        return np.array(blocksize,dtype=np.uint32)

    @property
    def dtype(self):
        dtype = self.OUTPUT.INFO.TYPE.VALUE
        return getattr(np,dtype,np.uint8)

    @property
    def bounds(self):
        get_val = lambda k: getattr(self.INPUT.POSITION,k).VALUE
        y0x0 = np.array(map(get_val,'YX'))
        y1x1 = y0x0 + self.shape
        return [y0x0, y1x1]

    @property
    def shape(self):
        get_val = lambda k: getattr(self.INPUT.POSITION,k).VALUE
        return map(get_val,['HEIGHT','WIDTH'])

    @property
    def scale(self):
        return float(2 ** self.INPUT.RESOLUTION.XY.VALUE)

    @property
    def scaled_bounds(self):
        scale = lambda b: (b // self.scale).astype(np.uint32)
        return map(scale, self.bounds)

    @property
    def tiled_bounds(self):
        raw_bounds = self.scaled_bounds
        float_block = self.blocksize.astype(np.float32)
        raw_start = raw_bounds[0] / float_block
        raw_end = raw_bounds[1] / float_block

        bounds_start = np.floor(raw_start).astype(np.uint32)
        bounds_end = np.ceil(raw_end).astype(np.uint32)
        return [bounds_start, bounds_end]

    @property
    def scaled_shape(self):
        scale = lambda b: int(b // self.scale)
        return map(scale, self.shape)

    @property
    def tiled_shape(self):
        return -np.subtract(*self.tiled_bounds)

    def scale_bounds(self, tile_index):
        tile_start = self.blocksize * tile_index
        tile_end = self.blocksize * (tile_index+1)
        return [tile_start, tile_end]

    def some_in_all(self, t_index):
        shape = self.scaled_shape
        origin = self.scaled_bounds[0]
        clip_off = lambda s: np.clip(s-origin,0,shape)
        return map(clip_off, self.scale_bounds(t_index))

    def all_in_some(self, t_index):
        shape = self.blocksize
        origin = self.scale_bounds(t_index)[0]
        clip_off = lambda s: np.clip(s-origin,0,shape)
        return map(clip_off, self.scaled_bounds)

