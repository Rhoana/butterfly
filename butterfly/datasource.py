import os
import re
import cv2
import h5py
import settings
import numpy as np

class DataSource(object):

    def __init__(self, core, datapath):
        '''
        '''
        self._core = core
        self._datapath = datapath
        self._size_x = -1
        self._size_y = -1
        self._size_z = -1
        # Maximum supported zoom in file system, affects calculations
        self.max_zoom = -1
        self.blocksize = (0, 0)
        self._color_map = None

    def index(self):
        '''
        Index all files without loading to
        create bounding box for this data.
        '''
        self.dtype = self.get_type()

    def get_type(self):
        return self.load(0,0,0,0).dtype

    def load_cutout(self, x0, x1, y0, y1, z, w):
        '''
        Load a cutout from a plane
        '''
        scale = float(2 ** w)
        blockshape = np.array(self.blocksize)
        x0y0 = np.array([x0,y0]) // scale
        x1y1 = np.array([x1,y1]) // scale
        top_left = np.floor(x0y0 / blockshape).astype(int)
        lo_right = np.ceil(x1y1 / blockshape).astype(int)
        origin = top_left * blockshape
        [left,top] = x0y0 - origin
        [right,down] = x1y1 - origin
        gridshape = lo_right-top_left
        grid = np.indices(gridshape).T

        cutshape = blockshape*grid.shape[:-1]
        cutout = np.zeros(cutshape, dtype=self.dtype)
        fixed = [z,w]
        for row in grid:
            for where in row:
                here = top_left + where
                [i0,j0] = blockshape*(where)
                [i1,j1] = blockshape*(where+1)
                one_tile = list(here)+fixed
                tile = self.load(*one_tile)
                cutout[j0:j1,i0:i1] = tile
        return cutout[top:down,left:right]

    def load(self, cur_path, w):
        '''
        Loads this file from the data path.
        '''

        cache_index = (cur_path, w)

        # Check if image in cache
        if cache_index in self._core._cache:
            # Move most recently accesed items to the top
            self._core._cache[cache_index] = self._core._cache.pop(cache_index)
            print 'Loading from cache!'
            return self._core._cache[cache_index]

        # Load image from given path, check extension
        tile_ext = cur_path.rpartition('.')[2]
        if tile_ext == 'hdf5':
            with h5py.File(cur_path, 'r') as f:
                datasets = []
                f.visit(datasets.append)
                tmp_image = f[datasets[0]][()]
        else:
            print 'Current path', cur_path
            tmp_image = cv2.imread(cur_path, 0)

        # Resize if necessary, then also store to cache
        if w > 0:
            # We will use subsampling for all requests right now for speed
            if settings.ALWAYS_SUBSAMPLE or self.dtype == np.uint32:
                # Subsample to preserve accuracy for segmentations
                tmp_image = tmp_image[::2 ** w, ::2 ** w]
            else:
                factor = 0.5 ** w
                tmp_image = cv2.resize(
                    tmp_image,
                    (0,
                     0),
                    fx=factor,
                    fy=factor,
                    interpolation=settings.IMAGE_RESIZE_METHOD)

        self._core._current_cache_size += tmp_image.size

        # If we don't care to exceed the max cache size temporarily:
        # self._core._cache[cur_path] = cv2.imread(cur_path, 0)
        # self._core._current_cache_size += self._core._cache[cur_path].size

        # Remove items in cache until everything fits
        while self._core._current_cache_size > self._core._max_cache_size:
            oldest_item = self._core._cache.keys()[0]
            self._core._current_cache_size -= self._core._cache[
                oldest_item].size
            del self._core._cache[oldest_item]

        self._core._cache[cache_index] = tmp_image

        return tmp_image

    def seg_to_color(self, slice):
        colors = np.zeros(slice.shape+(3,),dtype=np.uint8)
        colors[:,:,0] = np.mod(107*slice[:,:],700).astype(np.uint8)
        colors[:,:,1] = np.mod(509*slice[:,:],900).astype(np.uint8)
        colors[:,:,2] = np.mod(200*slice[:,:],777).astype(np.uint8)
        return colors

    def get_boundaries(self):
        '''
        Get maximum data size
        '''
        pass

    def get_channel(self,path):
        '''
        :param path: the root/path/to/this/data
        :returns: channel of meta info about self
        '''
        dimensions = dict(zip(('x','y','z'),self.get_boundaries()))
        return {
            'path': path,
            'name': os.path.basename(path),
            'dimensions': dimensions,
            'data-type': str(self.dtype)
        }
