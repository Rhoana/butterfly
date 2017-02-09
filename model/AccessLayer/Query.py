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
    def scale(self):
        return float(2 ** self.resolution)
    @property
    def bounds(self):
        x0y0 = np.array(self.x, self.y)
        x1y1 = x0y0 + [self.width,self.height]
        return [x0y0, x1y1]
    @property
    def scaled_bounds(self):
        return [b//self.scale for b in self.bounds]
    @property
    def indexed_bounds(self):
        x0y0,x1y1 = self.scaled_bounds
        bounds_start = np.floor(x0y0/self.blocksize).astype(int)
        bounds_end = np.ceil(x1y1/self.blocksize).astype(int)
        return [bounds_start, bounds_end]

    def index_offset(self, tile_index):
        indexed_origin = self.indexed_bounds[0]
        return tile_index - indexed_origin

    def scale_offset(self, tile_pixel):
        scaled_origin = self.scaled_bounds[0]
        return tile_pixel - scaled_origin


    def log(self,action,**kwargs):
        statuses = [
            'info': ['miss']
        ]
        actions ={
            'miss': 'Missing {lost} from {group}'
        }
        message = actions[action].format(**kwargs)
        status = next(s for s in statuses if action in s)
        getattr(logging, status)(message)
        return message
