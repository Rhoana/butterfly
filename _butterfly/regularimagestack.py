from datasource import Datasource
import os
import cv2

class RegularImageStack(Datasource):
  
  def __init__(self, datapath):
    '''
    @override
    '''

    super(RegularImageStack, self).__init__(datapath)

  def index(self):
    '''
    @override
    '''
    #self.blocksize = self.get_blocksize()

    super(RegularImageStack, self).index()

  def load_paths(self, folderpaths, filename, indices):
    self._folderpaths = folderpaths
    self._filename = filename
    self._indices = indices

  def get_blocksize():
    '''
    Placeholder function for now
    '''
    pass

  def load(self, x, y, z, w):
    '''
    @override
    '''

    cur_filename = self._filename % {'x': self._indices[0][x], 'y': self._indices[1][y], 'z': self._indices[2][z]}
    print cur_filename
    cur_path = os.path.join(self._datapath, self._folderpaths % {'z': self._indices[2][z]}, cur_filename)
    if w == 0:
        return super(RegularImageStack, self).load(cur_path)

    factor = 0.5**w
    return cv2.resize(super(RegularImageStack, self).load(cur_path),(0,0), fx=factor, fy=factor, interpolation=cv2.INTER_LINEAR)