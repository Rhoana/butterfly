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
        return self.INPUT.IMAGE.FORMAT.VALUE in ['zip']

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
        x0y0 = np.array(map(get_val,'XY'))
        x1y1 = x0y0 + self.shape
        return [x0y0, x1y1]

    @property
    def shape(self):
        get_val = lambda k: getattr(self.INPUT.POSITION,k).VALUE
        return map(get_val,['WIDTH','HEIGHT'])

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
        raw_start = raw_bounds[0] / self.blocksize
        raw_end = raw_bounds[1] / self.blocksize
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
        a_b = self.scaled_bounds
        s_b = self.scale_bounds(t_index)
        some_to_all = lambda s: np.clip(s-a_b[0],*a_b)
        return map(some_to_all, s_b)

    def all_in_some(self, t_index):
        a_b = self.scaled_bounds
        s_b = self.scale_bounds(t_index)
        all_to_some = lambda a: np.clip(a-s_b[0],*s_b)
        return map(all_to_some, a_b)

