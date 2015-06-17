import os

from regularimagestack import RegularImageStack

class Core(object):

  def __init__(self):
    '''
    '''
    self._datasources = {}


  def get(self, datapath, x1, x2, y1, y2, z1, z2, w=0):
    '''
    Request a subvolume of the datapath at a given zoomlevel.
    '''

    #
    # if datapath is not indexed (knowing the meta information like width, height),do it now
    if not datapath in self._datasources:
      self._datasources[datapath] = self.create_datasource(datapath)

    datasource = self._datasources[datapath]

    # else wise return the data
    #


    pass


  def create_datasource(self, datapath):
    '''
    '''

    # detect data source type

    # create specific datasource object
    ds = RegularImageStack(datapath)

    # call index
    ds.index()

    # return datasource object
    return ds
