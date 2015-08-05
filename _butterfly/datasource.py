import cv2
import h5py

class Datasource(object):

  def __init__(self, core, datapath):
    '''
    '''
    self._core = core
    self._datapath = datapath
    self._size_x = -1
    self._size_y = -1
    self._size_z = -1
    #Maximum supported zoom in file system, affects calculations
    self.max_zoom = -1
    
  def index(self):
    '''
    Index all files without loading to
    create bounding box for this data.
    '''
    pass

  def load(self, cur_path):
    '''
    Loads this file from the data path.
    '''
    #Check if image in cache
    if cur_path in self._core._cache:
        #Move most recently accesed items to the top
        self._core._cache[cur_path] = self._core._cache.pop(cur_path)
        return self._core._cache[cur_path]

    #Load image from given path
    if cur_path.rpartition('.')[2] == 'hdf5':
        with h5py.File(cur_path, 'r') as f:
            tmp_image = f['IdMap'][()]
    else:
        tmp_image = cv2.imread(cur_path, 0)

    self._core._current_cache_size += tmp_image.size

    #If we don't care to exceed the max cache size temporarily:
    #self._core._cache[cur_path] = cv2.imread(cur_path, 0)
    #self._core._current_cache_size += self._core._cache[cur_path].size

    #Remove items in cache until everything fits
    while self._core._current_cache_size > self._core._max_cache_size:
        oldest_item = self._core._cache.keys()[0]
        self._core._current_cache_size -= self._core._cache[oldest_item].size
        del self._core._cache[oldest_item]

    self._core._cache[cur_path] = tmp_image

    return tmp_image

