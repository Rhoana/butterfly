from ImageLayer import *
from Query import Query
import numpy as np

class TileQuery(Query):

    def __init__(self, *args, **keywords):

        query, zyx_index, kji_pixels = args
        source_list = self.RUNTIME.IMAGE.SOURCE.LIST

        self.SOURCES = {
            source_list[0]: HDF5,
            source_list[1]: TileSpecs,
            source_list[2]: Mojo,
            source_list[3]: ImageStack
        }

        self.RUNTIME.TILE.ZYX.VALUE = zyx_index
        self.RUNTIME.TILE.KJI.VALUE = kji_pixels
        self.RUNTIME.TILE.SCALES.VALUE = query.scales

        q_source = query.RUNTIME.IMAGE.SOURCE.VALUE
        q_block = query.RUNTIME.IMAGE.BLOCK.VALUE
        q_path = query.OUTPUT.INFO.PATH.VALUE

        self.RUNTIME.IMAGE.SOURCE.VALUE = q_source
        self.RUNTIME.IMAGE.BLOCK.VALUE = q_block
        self.OUTPUT.INFO.PATH.VALUE = q_path

    @property
    def key(self):
        origin = self.index_zyx
        scales = self.all_scales
        all_keys = np.r_[scales,origin]
        return np.array2string(all_keys)

    @property
    def source_class(self):
        disk_fmt = self.RUNTIME.IMAGE.SOURCE.VALUE
        return self.SOURCES.get(disk_fmt, HDF5)

    @property
    def all_scales(self):
        return np.uint32(self.RUNTIME.TILE.SCALES.VALUE)

    @property
    def pixels_kji(self):
        return np.uint32(self.RUNTIME.TILE.KJI.VALUE)

    @property
    def index_zyx(self):
        return np.uint32(self.RUNTIME.TILE.ZYX.VALUE)

    @property
    def blocksize(self):
        return np.uint32(self.RUNTIME.IMAGE.BLOCK.VALUE)

    @property
    def target_bounds(self):
        tile_origin = self.blocksize*self.index_zyx
        return  self.pixels_kji + tile_origin

    @property
    def target_origin(self):
        tile_origin = self.blocksize*self.index_zyx
        return  self.pixels_kji[0] + tile_origin

    @property
    def source_bounds(self):
        return self.all_scales * self.target_bounds

