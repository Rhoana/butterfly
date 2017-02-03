from datasource import DataSource
import dataspec
import numpy as np
from rh_logger import logger
from rh_renderer.models import AffineModel, Transforms
from rh_renderer.single_tile_renderer import SingleTileRendererBase
from rh_renderer.multiple_tiles_renderer import MultipleTilesRenderer
from scipy.spatial import KDTree
from urllib2 import HTTPError


class MultiBeam(DataSource):

    def __init__(self, core, datapath):
        '''
        @override
        '''

        if not dataspec.can_load(datapath):
            raise HTTPError(
                None, 404,
                "Failed to load %s as multibeam data source" % datapath,
                [], None)

        super(MultiBeam, self).__init__(core, datapath)

    def index(self):
        '''
        @override
        '''

        self.ts = {}
        self.coords = {}
        self.kdtrees = {}
        self.min_x = np.inf
        self.max_x = - np.inf
        self.min_y = np.inf
        self.max_y = - np.inf
        self.min_z = np.inf
        self.max_z = - np.inf
        for tilespec in dataspec.load(self._datapath):
            for ts in tilespec:
                bbox = ts.bbox
                x0 = bbox.x0
                x1 = bbox.x1
                y0 = bbox.y0
                y1 = bbox.y1
                center_x = (x0 + x1) / 2
                center_y = (y0 + y1) / 2
                layer = ts.layer
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
        self.tile_width = ts.width
        self.tile_height = ts.height
        self.blocksize = np.array((4096, 4096))
        logger.report_event(
            "Loaded %d x %d x %d space" %
            (self.max_x - self.min_x + 1,
             self.max_y - self.min_y + 1,
             self.max_z - self.min_z + 1))

        super(MultiBeam, self).index()

    def load_cutout(self, x0, x1, y0, y1, z, w):
        '''
        @override
        '''
        if z not in self.ts or len(self.ts[z]) == 0:
            return np.zeros((int((x1 - x0) / 2**w),
                             int((y1 - y0) / 2**w)), np.uint8)
        if hasattr(self.ts[z][0], "section"):
            section = self.ts[z][0].section
            return section.imread(x0, y0, x1, y1, w)
        return self.load_tilespec_cutout(x0, x1, y0, y1, z, w)

    def load_tilespec_cutout(self, x0, x1, y0, y1, z, w):
        '''Load a cutout from tilespecs'''
        kdtree = self.kdtrees[z]
        assert isinstance(kdtree, KDTree)
        x0a = x0 - self.tile_width / 2
        x1a = x1 + self.tile_width / 2
        y0a = y0 - self.tile_height / 2
        y1a = y1 + self.tile_height / 2
        nx = 2 * (x1a - x0a) / self.tile_width + 1
        ny = 2 * (y1a - y0a) / self.tile_height + 1
        xr = np.vstack([np.linspace(x0a, x1a, nx)] * ny)
        yr = np.column_stack([np.linspace(y0a, y1a, ny)] * nx)
        coords = np.column_stack([xr.flatten(), yr.flatten()])
        d, idxs = kdtree.query(coords)
        idxs = np.unique(idxs)
        single_renderers = []
        for idx in idxs:
            ts = self.ts[z][idx]
            transformation_models = []
            for ts_transform in ts.get_transforms():
                model = Transforms.from_tilespec(ts_transform)
                transformation_models.append(model)
            renderer = TilespecSingleTileRenderer(
                ts, transformation_models=transformation_models,
                compute_distances=False)
            single_renderers.append(renderer)
            if w > 0:
                model = AffineModel(m=np.eye(3) / 2.0 ** w)
                renderer.add_transformation(model)
        renderer = MultipleTilesRenderer(
            single_renderers, blend_type='AVERAGING', dtype=self.dtype)
        return renderer.crop(
            int(x0 / 2**w), int(y0 / 2**w), int(x1 / 2**w), int(y1 / 2**w))[0]


    def load(self, x, y, z, w):
        '''
        @override
        '''
        if z < self.min_z:
            z = self.min_z
        elif z > self.max_z:
            z = self.max_z

        if z not in self.kdtrees:
            return np.zeros(self.blocksize)

        x0 = x * self.blocksize[0]
        y0 = y * self.blocksize[0]
        x1 = x0 + self.blocksize[0]
        y1 = y0 + self.blocksize[1]
        logger.report_event(
            "Fetching x=%d:%d, y=%d:%d, z=%d" % (x0, x1, y0, y1, z))

        kdtree = self.kdtrees[z]
        assert isinstance(kdtree, KDTree)
        #
        # Look every "blocksize" within the kdtree for the closest center
        #
        nx = 2 * (x1 - x0) / self.tile_width + 1
        ny = 2 * (y1 - y0) / self.tile_height + 1
        xr = np.vstack([np.linspace(x0, x1, nx)] * ny)
        yr = np.column_stack([np.linspace(y0, y1, ny)] * nx)
        coords = np.column_stack([xr.flatten(), yr.flatten()])
        d, idxs = kdtree.query(coords)
        idxs = np.unique(idxs)
        single_renderers = []
        for idx in idxs:
            ts = self.ts[z][idx]
            renderer = TilespecSingleTileRenderer(
                ts, compute_distances=False,
                mipmap_level=w)
            single_renderers.append(renderer)
            if w > 0:
                model = AffineModel(m=np.eye(3) * 2.0 ** w)
                renderer.add_transformation(model)
            for ts_transform in ts.get_transforms():
                model = Transforms.from_tilespec(ts_transform)
                renderer.add_transformation(model)
            if w > 0:
                model = AffineModel(m=np.eye(3) / 2.0 ** w)
                renderer.add_transformation(model)
        renderer = MultipleTilesRenderer(single_renderers)
        return renderer.crop(
            x0 / 2**w, y0 / 2**w, x1 / 2**w, y1 / 2**w)[0]

    def get_boundaries(self):

        return self.max_x - self.min_x, self.max_y - self.min_y, self.max_z


class TilespecSingleTileRenderer(SingleTileRendererBase):
    '''SingleTileRenderer using tilespec to retrieve images'''

    def __init__(self, ts,
                 compute_mask=False,
                 compute_distances=True,
                 transformation_models=[],
                 mipmap_level=0):
        width = ts.width / 2 ** mipmap_level
        height = ts.height / 2 ** mipmap_level
        super(TilespecSingleTileRenderer, self).__init__(
            width, height, compute_mask=compute_mask, 
            transformation_models=transformation_models,
            compute_distances=compute_distances)
        self.ts = ts
        self.mipmap_level = mipmap_level

    def load(self):
        return self.ts.imread(mipmap_level=self.mipmap_level)
