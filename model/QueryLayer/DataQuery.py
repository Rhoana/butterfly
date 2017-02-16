from Query import Query
import numpy as np
import logging

class DataQuery(Query):

    def __init__(self,*args,**kwargs):

        # Add basic list of getters
        self.groups = map(self.grouper, self.rankings)
        self.X,self.Y,self.Z = self.position[:3]
        self.make_getter('tile_keys', '')
        self.make_getter('data_keys', '')
        self.make_getter('info_keys', '')
        self.make_getter('position', -1)
        self.make_getter('groups', '')

        # Set all raw attributes
        concat = lambda a,b: a+getattr(self,b)
        keys = [[],'tile_keys','info_keys','data_keys']
        keys = keys + ['position','groups']
        allkeys = reduce(concat, keys)
        havekeys = set(kwargs.keys())
        for key in set(allkeys) & havekeys:
            self.raw[key] = kwargs[key]

    def check(self):
        needs = set(self.position)
        haves = set(self.raw_key())
        lost_pos = list(needs - haves)
        if self.is_data and len(lost_pos):
            self.log('miss', lost=lost_pos, group='position')

    @property
    def key(self):
        get = lambda k: getattr(self,k)
        return '_'.join(map(get,self.groups))

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
        blocksize = getattr(self,self.BLOCK)
        if not len(blocksize):
            return np.array([512,512],dtype=np.uint16)
        return np.fromstring(blocksize,dtype=np.uint16)

    @property
    def dtype(self):
        dtype = getattr(self,self.TYPE)
        return getattr(np,dtype,np.uint8)

    @property
    def bounds(self):
        x0y0 = np.array([self.x, self.y])
        x1y1 = x0y0 + [self.width,self.height]
        return np.r_[x0y0, x1y1]

    @property
    def scale(self):
        return float(2 ** self.resolution)

    @property
    def scaled_bounds(self):
        return self.bounds // self.scale

    @property
    def indexed_bounds(self):
        raw_bounds = self.scaled_bounds
        raw_start = raw_bounds[:2] / self.blocksize
        raw_end = raw_bounds[2:] / self.blocksize
        bounds_start = np.floor(raw_start).astype(int)
        bounds_end = np.ceil(raw_end).astype(int)
        return np.r_[bounds_start, bounds_end]

    def tile_bounds(self, tile_index):
        tile_start = self.blocksize * tile_index
        tile_end = self.blocksize * (tile_index+1)
        return np.r_[tile_start, tile_end]

    def scale_offset(self, tile_pixel):
        scaled_origin = self.scaled_bounds[:2]
        return (tile_pixel - scaled_origin).astype(int)

