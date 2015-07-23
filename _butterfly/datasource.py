import cv2

class Datasource(object):

  def __init__(self, datapath):
    '''
    '''
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
    #Need to be able to throw errors!
    return cv2.imread(cur_path, 0)

