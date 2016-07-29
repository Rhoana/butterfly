from datasource import DataSource
import dataspec
import numpy as np
from rh_logger import logger
from rh_renderer.models import AffineModel, Transforms
from rh_renderer.tilespec_renderer import TilespecRenderer
from urllib2 import HTTPError
import glob
import os
import json
import logging
import numpy as np

class Tilespecs(DataSource):

    def __init__(self, core, datapath, dtype=np.uint8):
        '''
        @override
        '''

        if not dataspec.can_load(datapath):
            raise HTTPError(
                None, 404,
                "Failed to load %s as multibeam data source" % datapath,
                [], None)
        self.dtype=dtype
        super(Tilespecs, self).__init__(core, datapath)

    def index(self):
        '''
        @override
        '''

        self.layer_ts = {}
        self.layer_renderer = {}
        self.min_x = np.inf
        self.max_x = - np.inf
        self.min_y = np.inf
        self.max_y = - np.inf
        self.min_z = np.inf
        self.max_z = - np.inf
        ts_fnames = glob.glob(os.path.join(self._datapath, '*.json'))
        for ts_fname in ts_fnames:
            # Load the tilespecs from the file
            tilespecs = None
            with open(ts_fname, 'r') as data:
                tilespecs = json.load(data)

            if len(tilespecs) == 0:
                logger.report_event("no valid tilespecs in file {}, skipping".format(ts_fname), log_level=logging.WARN)
                continue

            layer = tilespecs[0]["layer"]
            self.min_z = min(self.min_z, layer)
            self.max_z = max(self.max_z, layer)
            self.layer_ts[layer] = tilespecs
            for ts in tilespecs:
                x_min, x_max, y_min, y_max = ts["bbox"]
                self.min_x = min(self.min_x, x_min)
                self.max_x = max(self.max_x, x_max)
                self.min_y = min(self.min_y, y_min)
                self.max_y = max(self.max_y, y_max)

            self.layer_renderer[layer] = TilespecRenderer(tilespecs, self.dtype)

        self.tile_width = ts["width"]
        self.tile_height = ts["height"]
        self.blocksize = np.array((4096, 4096))
        logger.report_event(
            "Loaded %d x %d x %d space" %
            (self.max_x - self.min_x + 1,
             self.max_y - self.min_y + 1,
             self.max_z - self.min_z + 1))

    def load_cutout(self, x0, x1, y0, y1, z, w):
        if z not in self.layer_ts or len(self.layer_ts[z]) == 0:
            super(Tilespecs, self).load_cutout(x0, x1, y0, y1, z, w)
        #if hasattr(self.ts[z][0], "section"):
        #    section = self.ts[z][0].section
        #    return section.imread(x0, y0, x1, y1, w)
        return self.load_tilespec_cutout(x0, x1, y0, y1, z, w)
    
    def load_tilespec_cutout(self, x0, x1, y0, y1, z, w):
        '''Load a cutout from tilespecs'''
        if w > 0:
            model = AffineModel(m=np.eye(3) / 2.0 ** w)
            self.layer_renderer[z].add_transformation(model)
        img, start_point = self.layer_renderer[z].crop(
            int(x0 / 2**w), int(y0 / 2**w), int(x1 / 2**w), int(y1 / 2**w))
        # TODO pad the image (left and top), if necessary
        # Removing the downsampling... TODO - this should be done with a temporary transformation so no need for upsampling all the time
        if w > 0:
            model = AffineModel(m=np.eye(3) * 2.0 ** w)
            self.layer_renderer[z].add_transformation(model)
        return img
        
        

    def load(self, x, y, z, w, segmentation=False):
        '''
        @override
        '''
        # TODO - need to understand how to implement
        pass

#        if z < self.min_z:
#            z = self.min_z
#        elif z > self.max_z:
#            z = self.max_z
#        if segmentation:
#            return np.zeros((self.blocksize[0] / 2**w,
#                             self.blocksize[1] / 2**w, 3))
#        if z not in self.kdtrees:
#            return np.zeros(self.blocksize)
#
#        x0 = x * self.blocksize[0]
#        y0 = y * self.blocksize[0]
#        x1 = x0 + self.blocksize[0]
#        y1 = y0 + self.blocksize[1]
#        logger.report_event(
#            "Fetching x=%d:%d, y=%d:%d, z=%d" % (x0, x1, y0, y1, z))
#
#        kdtree = self.kdtrees[z]
#        assert isinstance(kdtree, KDTree)
#        #
#        # Look every "blocksize" within the kdtree for the closest center
#        #
#        nx = 2 * (x1 - x0) / self.tile_width + 1
#        ny = 2 * (y1 - y0) / self.tile_height + 1
#        xr = np.vstack([np.linspace(x0, x1, nx)] * ny)
#        yr = np.column_stack([np.linspace(y0, y1, ny)] * nx)
#        coords = np.column_stack([xr.flatten(), yr.flatten()])
#        d, idxs = kdtree.query(coords)
#        idxs = np.unique(idxs)
#        single_renderers = []
#        for idx in idxs:
#            ts = self.ts[z][idx]
#            renderer = TilespecSingleTileRenderer(
#                ts, compute_distances=False,
#                mipmap_level=w)
#            single_renderers.append(renderer)
#            if w > 0:
#                model = AffineModel(m=np.eye(3) * 2.0 ** w)
#                renderer.add_transformation(model)
#            for ts_transform in ts.get_transforms():
#                model = Transforms.from_tilespec(ts_transform)
#                renderer.add_transformation(model)
#            if w > 0:
#                model = AffineModel(m=np.eye(3) / 2.0 ** w)
#                renderer.add_transformation(model)
#        renderer = MultipleTilesRenderer(single_renderers)
#        return renderer.crop(
#            x0 / 2**w, y0 / 2**w, x1 / 2**w, y1 / 2**w)[0]

    def seg_to_color(self, slice):
        '''
        @override
        '''

        return slice

    def get_boundaries(self):
        '''
        @override
        '''

        return self.max_x - self.min_x, self.max_y - self.min_y, self.max_z


#class TilespecSingleTileRenderer(SingleTileRendererBase):
#    '''SingleTileRenderer using tilespec to retrieve images'''
#
#    def __init__(self, ts,
#                 compute_mask=False,
#                 compute_distances=True,
#                 mipmap_level=0):
#        width = ts.width / 2 ** mipmap_level
#        height = ts.height / 2 ** mipmap_level
#        super(TilespecSingleTileRenderer, self).__init__(
#            width, height, compute_mask, compute_distances)
#        self.ts = ts
#        self.mipmap_level = mipmap_level
#
#    def load(self):
#        return self.ts.imread(mipmap_level=self.mipmap_level)
