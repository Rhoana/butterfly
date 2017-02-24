from ImageLayer import *
from Query import Query
import numpy as np

class TileQuery(Query):

    def __init__(self, *args, **keywords):

        query, xy_index, start, end = args
        source_list = self.RUNTIME.IMAGE.SOURCE.LIST

        self.SOURCES = {
            source_list[0]: HDF5,
            source_list[1]: TileSpecs,
            source_list[2]: Mojo,
            source_list[3]: ImageStack
        }
        run_tile = self.RUNTIME.TILE.INSIDE
        out_tile = self.RUNTIME.TILE.OUTSIDE

        out_tile.Z.VALUE = int(0)
        out_tile.Y.VALUE = xy_index[0]
        out_tile.X.VALUE = xy_index[1]
        run_tile.K.VALUE = np.array([0,1])
        run_tile.J.VALUE = np.array([start[0],end[0]])
        run_tile.I.VALUE = np.array([start[1],end[1]])
        run_tile.SI.VALUE = int(query.scale)
        run_tile.SJ.VALUE = int(query.scale)
        run_tile.SK.VALUE = int(1)

        q_source = query.RUNTIME.IMAGE.SOURCE.VALUE
        q_block = query.RUNTIME.IMAGE.BLOCK.VALUE
        q_z = query.RUNTIME.TILE.OUTSIDE.Z.VALUE
        q_path = query.OUTPUT.INFO.PATH.VALUE

        self.RUNTIME.IMAGE.SOURCE.VALUE = q_source
        self.RUNTIME.IMAGE.BLOCK.VALUE = q_block
        self.RUNTIME.TILE.OUTSIDE.Z.VALUE = q_z
        self.OUTPUT.INFO.PATH.VALUE = q_path

    @property
    def key(self):
        all_keys = self.full_coords
        all_keys.append(self.all_scales)
        coord = np.concatenate(all_keys)
        return '_'.join(map(str,coord))

    @property
    def source_class(self):
        disk_fmt = self.RUNTIME.IMAGE.SOURCE.VALUE
        return self.SOURCES.get(disk_fmt, HDF5)

    @property
    def all_scales(self):
        run_tile = self.RUNTIME.TILE.INSIDE
        get_val = lambda k: getattr(run_tile,k).VALUE
        return map(get_val,['SK','SJ','SI'])

    @property
    def pixels_kji(self):
        run_tile = self.RUNTIME.TILE.INSIDE
        get_val = lambda k: getattr(run_tile,k).VALUE
        return map(get_val,'KJI')

    @property
    def index_zyx(self):
        runtime = self.RUNTIME.TILE.OUTSIDE
        get_val = lambda k: getattr(runtime,k).VALUE
        return map(get_val,'ZYX')

    @property
    def blocksize(self):
        return self.RUNTIME.IMAGE.BLOCK.VALUE

    @property
    def full_coords(self):
        Z,Y,X = self.index_zyx
        K,J,I = self.pixels_kji
        by, bx = self.blocksize
        bz = 1
        sk, sj, si = self.all_scales
        tz, ty, tx = [Z*bz +K, Y*by +J, X*bx + I]
        return [tz*sk, ty*sj, tx*si]


