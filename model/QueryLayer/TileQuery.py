from ImageLayer import *
from Query import Query

class TileQuery(Query):

    HDF5 = HDF5()
    MOJO = Mojo()
    SPECS = TileSpecs()
    STACK = ImageStack()

    def __init__(self, *args, **kwargs):

        self.SOURCES = {
            self.READ_LIST[0]: self.HDF5,
            self.READ_LIST[1]: self.SPECS,
            self.READ_LIST[2]: self.MOJO,
            self.READ_LIST[3]: self.STACK
        }

        query,xy_index,start,end = args
        self.S,self.I,self.J = self.TILE_LIST[:3]
        self.X,self.Y,self.Z = self.SPACE_LIST[:3]
        self.make_getter('SPACE_LIST', -1)
        self.make_getter('TILE_LIST', '')
        self.make_getter('DATA_LIST', '')
        self.raw = {
            self.X: xy_index[1],
            self.Y: xy_index[0],
            self.I: [start[0],end[0]],
            self.J: [start[1],end[1]],
            self.S: int(query.scale)
        }
        for k in ['PATH','BLOCK','DISK','Z']:
            term = getattr(self,k)
            self.raw[term] = getattr(query,term)

    @property
    def key(self):
        sijxyz = map(self.getatt,'SIJXYZ')
        return '_'.join(map(str,sijxyz))

    @property
    def source_class(self):
        disk_fmt = self.att(self.DISK)
        return self.SOURCES.get(disk_fmt,self.HDF5)

    @property
    def SIJ(self):
        return map(self.getatt,'SIJ')

    @property
    def XYZ(self):
        return map(self.getatt,'XYZ')


