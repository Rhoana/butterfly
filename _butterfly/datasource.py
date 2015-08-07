import cv2
import h5py
import settings

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
        pass

    def load(self, cur_path, w, segmentation=False):
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
            tmp_image = cv2.imread(cur_path, 0)

        # Resize if necessary, then also store to cache
        print 'RESIZE'

        if w > 0:
            # We will use subsampling for all requests right now for speed
            if settings.ALWAYS_SUBSAMPLE or segmentation:
                # Subsample to preserve accuracy for segmentations
                tmp_image = tmp_image[::2 ** w, ::2 ** w]
            else:
                factor = 0.5 ** w
                tmp_image = cv2.resize(tmp_image, (0, 0), fx=factor, fy=factor, interpolation=settings.IMAGE_RESIZE_METHOD)

        self._core._current_cache_size += tmp_image.size

        # If we don't care to exceed the max cache size temporarily:
        # self._core._cache[cur_path] = cv2.imread(cur_path, 0)
        # self._core._current_cache_size += self._core._cache[cur_path].size

        # Remove items in cache until everything fits
        while self._core._current_cache_size > self._core._max_cache_size:
            oldest_item = self._core._cache.keys()[0]
            self._core._current_cache_size -= self._core._cache[oldest_item].size
            del self._core._cache[oldest_item]

        self._core._cache[cache_index] = tmp_image

        return tmp_image

    def seg_to_color(self):
        '''
        Get segmentation color from color map
        '''
        pass

    def get_boundaries(self):
        '''
        Get maximum data size
        '''
        pass
