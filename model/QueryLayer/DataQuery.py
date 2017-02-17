from Query import Query
import numpy as np
import logging

class DataQuery(Query):

    def __init__(self,*args,**kwargs):

        # Add basic list of getters
        self.X,self.Y,self.Z = self.SPACE_LIST[:3]
        self.W,self.H,self.D,self.R = self.SPACE_LIST[3:]
        self.make_getter('TILE_LIST', '')
        self.make_getter('DATA_LIST', '')
        self.make_getter('INFO_LIST', '')
        self.make_getter('SPACE_LIST', -1)
        self.make_getter('GROUP_LIST', '')
        self.make_getter('SOURCE_LIST', '')

        # Set all raw attributes
        concat = lambda a,b: a+getattr(self,b)
        keys = [[],'TILE_LIST','INFO_LIST','DATA_LIST']
        keys = keys + ['SOURCE_LIST','SPACE_LIST','GROUP_LIST']
        allkeys = reduce(concat, keys)
        havekeys = set(kwargs.keys())
        for key in set(allkeys) & havekeys:
            self.raw[key] = kwargs[key]

    def check(self):
        needs = set(self.SPACE_LIST)
        haves = set(self.raw.key())
        lost_pos = list(needs - haves)
        if self.is_data and len(lost_pos):
            self.log('miss', lost=lost_pos, group='position')

    @property
    def key(self):
        return '_'.join(map(self.att,self.GROUP_LIST))

    @property
    def is_zip(self):
        return self.att(self.FORM) in ['zip']

    @property
    def content_type(self):
        is_img = not self.is_zip
        fmt = self.att(self.FORM)
        content_type = self.content_types[is_img]
        return content_type.replace('{fmt}', fmt)

    @property
    def blocksize(self):
        blocksize = self.att(self.BLOCK)
        if not len(blocksize):
            return np.array([512,512],dtype=np.uint32)
        return np.fromstring(blocksize,dtype=np.uint32)

    @property
    def dtype(self):
        dtype = self.att(self.TYPE)
        return getattr(np,dtype,np.uint8)

    @property
    def bounds(self):
        x0y0 = np.array(map(self.getatt,'XY'))
        x1y1 = x0y0 + map(self.getatt,'WH')
        return [x0y0, x1y1]

    @property
    def shape(self):
        return map(self.getatt,'WH')

    @property
    def scale(self):
        return float(2 ** self.att(self.R))

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

