import numpy as np
import logging

class Query(object):
    methods = ['feature','format','view','id']
    unknown = ['datapath','blocksize','disk_format']
    groups = ['experiment','sample','dataset','channel']
    box = ['x','y','z','height','width','depth','resolution']
    raw = {
        'format': 'json',
        'feature': 'data',
        'view': 'grayscale'
    }
    def __init__(self,**kwargs):
        allkeys = self.unknown + self.methods
        self.allkeys = allkeys + self.groups + self.box
        rawlist = set(self.allkeys) & set(kwargs.keys())
        for key in rawlist:
            self.raw[key] = kwargs[key]

    def check(self):
        lost_box = list(set(self.box)-set(self.raw.key()))
        if self.is_data and len(lost_box):
            self.log('miss',lost=lost_box,group='box')

    @property
    def is_data(self):
        return self.feature in ['data']

    @property
    def is_zip(self):
        return self.format in ['zip']

    @property
    def content_type(self):
        content_types = [
            'application/{fmt}',
            'image/{fmt}',
        ]
        fmt = self.raw['format']
        is_img = self.is_data and not self.is_zip
        content_type = content_types[is_img]
        return content_type.replace('{fmt}', fmt)

    def update(self, key, value):
        if key in self.allkeys:
            self.raw[key] = value

    @property
    def feature(self):
        return self.raw.get('feature','')
    @property
    def format(self):
        return self.raw.get('format','')
    @property
    def view(self):
        return self.raw.get('view','')
    @property
    def id(self):
        return self.raw.get('id',-1)

    @property
    def datapath(self):
        return self.raw.get('datapath','')
    @property
    def blocksize(self):
        return self.raw.get('blocksize',[])
    @property
    def disk_format(self):
        return self.raw.get('disk_format','')

    @property
    def experiment(self):
        return self.raw.get('experiment','')
    @property
    def sample(self):
        return self.raw.get('sample','')
    @property
    def dataset(self):
        return self.raw.get('dataset','')
    @property
    def channel(self):
        return self.raw.get('channel','')

    @property
    def x(self):
        return self.raw.get('x',-1)
    @property
    def y(self):
        return self.raw.get('y',-1)
    @property
    def z(self):
        return self.raw.get('z',-1)

    @property
    def resolution(self):
        return self.raw.get('resolution',-1)
    @property
    def width(self):
        return self.raw.get('width',-1)
    @property
    def height(self):
        return self.raw.get('height',-1)
    @property
    def depth(self):
        return self.raw.get('depth',-1)

    @property
    def bounds(self):
        x0y0 = np.array(self.x, self.y)
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
        raw_bounds = self.scaled_bounds / self.blocksize
        bounds_start = np.floor(raw_bounds[:2]).astype(int)
        bounds_end = np.ceil(raw_bounds[2:]).astype(int)
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
