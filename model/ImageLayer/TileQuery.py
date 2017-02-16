from Settings import *

class TileQuery():
    position = POSITION
    tile_keys = TILETERMS
    data_keys = DATATERMS
    BLOCK = DATATERMS[1]
    PATH = TILETERMS[2]
    DISK = TILETERMS[3]
    raw = {}

    def __init__(self, query, xy_index):

        self.X,self.Y,self.Z = POSITION[:3]
        self.W,self.H,self.R = POSITION[3:]
        self.make_getter('position', -1)
        self.make_getter('tile_keys', '')
        self.make_getter('data_keys', '')
        self.raw = {
            self.X: xy_index[1],
            self.Y: xy_index[0],
            self.W: 512,
            self.H: 512
        }
        for k in ['PATH','BLOCK','DISK','Z','R']:
            term = getattr(self,k)
            self.raw[term] = getattr(query,term)

    def get_getter(self, _pos, _default):
        return lambda self: self.raw.get(_pos,_default)

    def make_getter(self, _list, _default):
        for pos in getattr(self, _list, []):
            getter = self.get_getter(pos, _default)
            setattr(TileQuery, pos, property(getter))

    @property
    def key(self):
        get = lambda k: str(getattr(self,getattr(self,k)))
        return '_'.join(map(get,'RHWXYZ'))
