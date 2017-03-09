from ImageLayer import *
from Query import Query
import numpy as np
import sys
import os

class TileQuery(Query):

    def __init__(self, *args, **keywords):

        Query.__init__(self, **keywords)

        query, zyx_index, kji_pixels = args
        self.source_list = self.RUNTIME.IMAGE.SOURCE.LIST

        self.SOURCES = {
            self.source_list[0]: HDF5,
            self.source_list[1]: TileSpecs,
            self.source_list[2]: Mojo,
            self.source_list[3]: ImageStack
        }

        self.RUNTIME.TILE.ZYX.VALUE = zyx_index
        self.RUNTIME.TILE.KJI.VALUE = kji_pixels
        self.RUNTIME.TILE.SCALES.VALUE = query.scales

        q_block = query.RUNTIME.IMAGE.BLOCK.VALUE
        self.RUNTIME.IMAGE.BLOCK.VALUE = q_block

        q_path = query.OUTPUT.INFO.PATH.VALUE
        self.OUTPUT.INFO.PATH.VALUE = q_path

        # Very important to get the right datasource
        query_source = query.RUNTIME.IMAGE.SOURCE
        self_source = self.RUNTIME.IMAGE.SOURCE
        self_source.VALUE = query_source.VALUE

        # Only applies to HDF5 datasource
        query_H5 = query.RUNTIME.IMAGE.SOURCE.HDF5.INNER
        self_H5 = self.RUNTIME.IMAGE.SOURCE.HDF5.INNER
        self_H5.VALUE = query_H5.VALUE


    @property
    def key(self):
        origin = self.index_zyx
        scales = self.all_scales
        tile_values = np.r_[scales,origin]
        tile_key =  np.array2string(tile_values)
        return self.path + tile_key

    @property
    def tile(self):
        return self.my_source.load_tile(self)

    @property
    def path(self):
        return self.OUTPUT.INFO.PATH.VALUE

    @property
    def my_source(self):
        my_source = self.RUNTIME.IMAGE.SOURCE.VALUE
        return self.get_source(my_source)

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
    def tile_origin(self):
        return self.blocksize*self.index_zyx

    @property
    def target_origin(self):
        return  self.pixels_kji[0] + self.tile_origin

    @property
    def target_bounds(self):
        return  self.pixels_kji + self.tile_origin

    @property
    def source_bounds(self):
        return self.all_scales * self.target_bounds

    @property
    def preload_source(self):
        # Get all the metadata needed for the cache
        cache_meta = self.RUNTIME.CACHE.META
        # Preload the metadata from the source
        keywords = self.valid_source

        # Get the size of this dicitonary for the cache
        dict_size = np.uint32(sys.getsizeof({}))
        keywords[cache_meta.NAME] = dict_size
        # calculate the size
        for key in keywords.keys():
            n_bytes = sys.getsizeof(keywords[key])
            keywords[cache_meta.NAME] += n_bytes
        # Return keywords for cache and dataQuery
        return keywords

    @property
    def valid_source(self):
        # Get the path key and value
        k_path = self.OUTPUT.INFO.PATH.NAME
        v_path = self.OUTPUT.INFO.PATH.VALUE
        # Make sure we have a valid pathname
        is_path = os.path.exists(v_path)
        msg = 'a valid path for butterfly'
        self.check_any(is_path,msg,v_path,k_path)
        # Get the default source
        my_source = self.RUNTIME.IMAGE.SOURCE
        # Validate the source of self.path
        for name in self.source_list:
            source = self.get_source(name)
            # Ask if source can load self path
            keywords = source.preload_source(self)
            if len(keywords):
                # Set valid source
                keywords[my_source.NAME] = name
                return keywords
        # return empty
        return {}

    def get_source(self,name):
        return self.SOURCES.get(name, HDF5)
