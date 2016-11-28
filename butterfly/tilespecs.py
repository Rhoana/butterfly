from rh_renderer.tilespec_renderer import TilespecRenderer
from rh_renderer.models import AffineModel, Transforms
from datasource import DataSource
from urllib2 import HTTPError
from rh_logger import logger
from copy import deepcopy
import numpy as np
import dataspec
import logging
import json
import glob
import os

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

        super(Tilespecs, self).index()

    def get_type(self):
        '''
        @override
        '''
        return self.load(0,0,0,0).crop(0,0,1,1)[0].dtype

    def load_cutout(self, x0, x1, y0, y1, z, w):
        '''
        @override
        '''
        cutout_bounds = (np.array([x0, y0, x1, y1])/(2.0 ** w)).astype(np.uint32)
        img = self.load(0,0,z,w).crop(*cutout_bounds)[0]
        return img

    def load(self, x, y, z, w):
        '''
        @override
        '''
        plane_rendered = deepcopy(self.layer_renderer[z])
        if w > 0:
            model = AffineModel(m=np.eye(3) / 2.0 ** w)
            plane_rendered.add_transformation(model)

        return plane_rendered

    def get_boundaries(self):

        return self.max_x - self.min_x, self.max_y - self.min_y, self.max_z
