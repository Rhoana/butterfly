from datasource import Datasource
import os

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

  def load(self, x, y, z):
    '''
    @override
    '''

    cur_filename = self._filename % {'x': self._indices[0][x], 'y': self._indices[1][y], 'z': self._indices[2][z]}
    cur_path = os.path.join(self._datapath, self._folderpaths % {'z': self._indices[2][z]}, cur_filename)

    return super(RegularImageStack, self).load(cur_path)
