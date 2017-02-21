from ImageLayer import *
from Query import Query

class TileQuery(Query):

    def __init__(self, *args, **kwargs):

        Query.__init__(self, **_keywords)
        query, xy_index, start, end = args
        source_list = self.RUNTIME.SOURCE.LIST

        self.SOURCES = {
            source_list[0]: HDF5,
            source_list[1]: TileSpecs,
            source_list[2]: Mojo,
            source_list[3]: ImageStack
        }
        run_tile = self.RUNTIME.TILE

        self.RUNTIXE.X.VALUE = xy_index[1]
        self.RUNTIME.Y.VALUE = xy_index[0]
        run_tile.I.VALUE = [start[0],end[0]]
        run_tile.J.VALUE = [start[1],end[1]]
        run_tile.SI.VALUE = query.scale
        run_tile.SJ.VALUE = query.scale
        run_tile.SK.VALUE = query.scaled_shape

        self.set_key(self.OUTPUT.INFO,'PATH')
        self.set_key(self.RUNTIME.IMAGE,'SOURCE')
        self.set_key(self.RUNTIME,'Z')

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


