from datasource import DataSource
import logging
import os
import cv2
import glob
import h5py
import numpy as np
import settings
import sys
from rh_aligner.common.utils import load_tilespecs, index_tilespec
from rh_renderer.models import Transforms
from rh_renderer.multiple_tiles_renderer\
     import MultipleTilesRenderer
from rh_renderer.single_tile_renderer\
     import SingleTileRenderer

from scipy.spatial import KDTree

logger = logging.getLogger(name="MultiBeam")
class MultiBeam(DataSource):

    def __init__(self, core, datapath):
        '''
        @override
        '''
        if datapath not in settings.MULTIBEAM["datasets"]:
            raise IndexError(
                "%s is not one of the datasets, \"%s\"" % 
                (datapath, '", "'.join(settings.MULTIBEAM["datasets"].keys())))
        super(MultiBeam, self).__init__(core, datapath)
        self.blocksize = np.array((1024, 1024))

    def index(self):
        '''
        @override
        '''
        tilespec_dir = os.path.join(
            settings.MULTIBEAM["datasets"][self._datapath], "tilespecs")
        self.tilespecs = []
        for tilespec_filename in os.listdir(tilespec_dir):
            logger.info("Loading tilespec %s" % tilespec_filename)
            try:
                self.tilespecs.append(load_tilespecs(
                    os.path.join(tilespec_dir, tilespec_filename)))
            except:
                logger.warn("Failed to load tilespec %s" % tilespec_filename)
        self.ts = {}
        self.coords = {}
        self.kdtrees = {}
        self.min_x = np.inf
        self.max_x = - np.inf
        self.min_y = np.inf
        self.max_y = - np.inf
        self.min_z = np.inf
        self.max_z = - np.inf
        for tilespec in self.tilespecs:
            for ts in tilespec:
                x0, x1, y0, y1 = ts["bbox"]
                center_x = (x0 + x1)/2
                center_y = (y0 + y1)/2
                layer = ts["layer"]
                if layer not in self.coords:
                    self.coords[layer] = []
                    self.ts[layer] = []
                self.coords[layer].append((center_x, center_y))
                self.ts[layer].append(ts)
                self.min_x = min(self.min_x, x0)
                self.max_x = max(self.max_x, x1)
                self.min_y = min(self.min_y, y0)
                self.max_y = max(self.max_y, y1)
                self.min_z = min(self.min_z, layer)
                self.max_z = max(self.max_z, layer)
        for layer in self.coords:
            coords = self.coords[layer] = np.array(self.coords[layer])
            self.kdtrees[layer] = KDTree(np.array(coords))
        self.tile_width = ts["width"]
        self.tile_height = ts["height"]

    def load(self, x, y, z, w, segmentation=False):
        '''
        @override
        '''
        if z < self.min_z:
            z = self.min_z
        elif z > self.max_z:
            z = self.max_z
        if segmentation:
            return np.zeros((self.blocksize[0], self.blocksize[1], 3))
        if z not in self.kdtrees:
            return np.zeros(self.blocksize)
            
        x0 = x*self.blocksize[0] + (self.max_x + self.min_x) / 2
        y0 = y*self.blocksize[0] + (self.max_y + self.min_y) / 2
        x1 = x0 + self.blocksize[0]
        y1 = y0 + self.blocksize[1]
        logger.info("Fetching x=%d:%d, y=%d:%d, z=%d" % (x0, x1, y0, y1, z))
        
        kdtree = self.kdtrees[z]
        assert isinstance(kdtree, KDTree)
        d, idxs = kdtree.query(np.array([[x0, y0],
                                         [x1, y0],
                                         [x0, y1],
                                         [y0, y1]]))
        idxs = np.unique(idxs)
        single_renderers = []
        for idx in idxs:
            ts = self.ts[z][idx]
            # TODO - make use of mipmap levels
            url = ts["mipmapLevels"]['0']["imageUrl"]
            if url.startswith("file:"):
                url = url.split(":", 1)[1]
            renderer = SingleTileRenderer(
                url, ts["width"], ts["height"])
            single_renderers.append(renderer)
            for ts_transform in ts.get("transforms", []):
                model = Transforms.from_tilespec(ts_transform)
                renderer.add_transformation(model)
        renderer = MultipleTilesRenderer(single_renderers)
        return renderer.crop(x0, y0, x1, y1)[0][::2**w, ::2**w]

    def seg_to_color(self, slice):
        # super(MultiBeam, self).seg_to_color()

        return slice

    def get_boundaries(self):
        # super(MultiBeam, self).get_boundaries()

        return self.max_x-self.min_x, self.max_y-self.min_y, self.max_z