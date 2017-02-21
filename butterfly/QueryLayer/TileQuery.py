from ImageLayer import *
from Query import Query

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
        run_tile = self.RUNTIME.TILE

        self.RUNTIME.X.VALUE = xy_index[1]
        self.RUNTIME.Y.VALUE = xy_index[0]
        run_tile.I.VALUE = [start[0],end[0]]
        run_tile.J.VALUE = [start[1],end[1]]
        run_tile.SI.VALUE = int(query.scale)
        run_tile.SJ.VALUE = int(query.scale)
        run_tile.SK.VALUE = int(query.scale)

        q_path = query.OUTPUT.INFO.PATH.VALUE
        q_source = query.RUNTIME.IMAGE.SOURCE.VALUE
        q_z = query.RUNTIME.Z.VALUE

        self.OUTPUT.INFO.PATH.VALUE = q_path
        self.RUNTIME.IMAGE.SOURCE.VALUE = q_source
        self.RUNTIME.Z.VALUE = q_z

    @property
    def key(self):
        sij_xyz = self.pixels_sij + self.index_xyz
        return '_'.join(map(str,sij_xyz))

    @property
    def source_class(self):
        disk_fmt = self.RUNTIME.IMAGE.SOURCE.VALUE
        return self.SOURCES.get(disk_fmt, HDF5)

    @property
    def pixels_sij(self):
        run_tile = self.RUNTIME.TILE
        get_val = lambda k: getattr(run_tile,k).VALUE
        return map(get_val,['SI','I','J'])

    @property
    def index_xyz(self):
        runtime = self.RUNTIME
        get_val = lambda k: getattr(runtime,k).VALUE
        return map(get_val,'XYZ')


