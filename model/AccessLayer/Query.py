from Settings import *
import numpy as np
import logging

class Query():
    rankings = RANKINGS[:-1]
    METADATA = RANKINGS[-1]
    tile_keys = TILETERMS
    data_keys = DATATERMS
    info_keys = INFOTERMS
    position = POSITION
    PATH = TILETERMS[2]
    TYPE = DATATERMS[0]
    BLOCK = DATATERMS[1]
    NAME = INFOTERMS[0]
    raw = {}

    def __init__(self,**kwargs):

        # Add basic list of getters
        self.groups = map(self._get_group, self.rankings)
        self.X,self.Y,self.Z = self.position[:3]
        self.make_getter('tile_keys', '')
        self.make_getter('data_keys', '')
        self.make_getter('info_keys', '')
        self.make_getter('position', -1)
        self.make_getter('groups', '')

        # Set all raw attributes
        self.allkeys = self.tile_keys + self.info_keys
        self.allkeys = self.allkeys + self.groups + self.position
        rawlist = set(self.allkeys) & set(kwargs.keys())
        for key in rawlist:
            self.raw[key] = kwargs[key]

    def _get_group(self, _method):
        return GROUPINGS.get(_method,'')

    def get_getter(self, _pos, _default):
        return lambda self: self.raw.get(_pos,_default)

    def make_getter(self, _list, _default):
        for pos in getattr(self, _list, []):
            getter = self.get_getter(pos, _default)
            setattr(Query, pos, property(getter))

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
    def is_data(self):
        return self.method in ['data']

    @property
    def is_zip(self):
        return self.format in ['zip']

    @property
    def content_type(self):
        content_types = [
            'application/{fmt}',
            'image/{fmt}',
        ]
        fmt = self.format
        is_img = self.is_data and not self.is_zip
        content_type = content_types[is_img]
        return content_type.replace('{fmt}', fmt)

    @property
    def result(self):
        if self.method in self.rankings:
            return self.list
        if self.method in [self.METADATA]:
            return {
                self.PATH: getattr(self,self.PATH),
                self.TYPE: getattr(self,self.TYPE),
                'dimensions': {
                    self.X: self.x,
                    self.Y: self.y,
                    self.Z: self.z
                },
                self.NAME: self.name
            }
        return self.list

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

    def log(self,action,**kwargs):
        statuses = {
            'miss': 'info'
        }
        actions ={
            'miss': 'Missing {lost} from {group}'
        }
        status = statuses[action]
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
