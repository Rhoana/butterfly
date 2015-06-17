import cv2

class Datasource(object):

  def __init__(self, datapath):
    '''
    '''
    self._datapath = datapath
    self._size_x = -1
    self._size_y = -1
    self._size_z = -1

    
  def index(self):
    '''
    Index all files without loading to
    create bounding box for this data.
    '''
    pass

  def load(self, x, y, z):
    '''
    Loads this file from the data path.
    '''
    pass

