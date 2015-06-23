import os
import numpy as np

from regularimagestack import RegularImageStack

class Core(object):

  def __init__(self):
    '''
    '''
    self._datasources = {}

    #Is there a way not to initialize these temporary variables?
    self.vol_xy_start = [0, 0]
    self.tile_xy_start = [0, 0]

  def get(self, datapath, start_coord, vol_size, w=0):
    '''
    Request a subvolume of the datapath at a given zoomlevel.
    '''

    #
    # if datapath is not indexed (knowing the meta information like width, height),do it now
    if not datapath in self._datasources:
      self.create_datasource(datapath)

    datasource = self._datasources[datapath]

    # else wise return the data
    #

    vol = np.zeros(vol_size, dtype='uint32') #Do we need to support color as well?
    block_size = datasource.blocksize

    #Loop through all z-slices requested, using x,y offsets to calculate distance until next block or volume end
    for z in range(vol_size[2]):
      #Calculate list of tiles that we need
      x_tiles = range((start_coord[0]//block_size[0]), (((start_coord[0] + vol_size[0])//block_size[0]) + 1))
      y_tiles = range((start_coord[1]//block_size[1]), (((start_coord[1] + vol_size[1])//block_size[1]) + 1))

      #Reset the x-starting coordinate for the next row of calculations
      self.vol_xy_start[0] = 0
      self.tile_xy_start[0] = (start_coord[0]%block_size[0])
      for x in x_tiles:
        x_offset = min((block_size[0] - self.tile_xy_start[0]),(vol_size[0] - self.vol_xy_start[0]))

        #Reset the y-starting coordinate for the next column of areas
        self.vol_xy_start[1] = 0
        self.tile_xy_start[1] = (start_coord[1]%block_size[1])

        for y in y_tiles:
          y_offset = min((block_size[1] - self.tile_xy_start[1]),(vol_size[1] - self.vol_xy_start[1]))
          cur_img = datasource.load(x, y, z + start_coord[2])

          #Temporary code to show which cutouts we are grabbing and from where
          print 'tile:       ' + '(' + str(x) + ', ' + str(y) + ')' 
          print 'z slice:    ' + str(z + start_coord[2])
          print 'vol start:  ' + str(self.vol_xy_start)
          print 'tile start: ' + str(self.tile_xy_start)
          print 'x offset:   ' + str(x_offset)
          print 'y offset:   ' + str(y_offset) + '\n'

          #Add offsets in current y direction
          vol[self.vol_xy_start[0]:self.vol_xy_start[0] + x_offset, self.vol_xy_start[1]:self.vol_xy_start[1] + y_offset, z] = cur_img[self.tile_xy_start[0]:self.tile_xy_start[0] + x_offset, self.tile_xy_start[1]:self.tile_xy_start[1] + y_offset]
          self.tile_xy_start[1] = (self.tile_xy_start[1] + y_offset) % block_size[1]
          self.vol_xy_start[1] += y_offset

        #Add offsets in current x direction
        self.tile_xy_start[0] = (self.tile_xy_start[0] + x_offset) % block_size[0]
        self.vol_xy_start[0] += x_offset

    return vol



  def create_datasource(self, datapath):
    '''
    '''

    # detect data source type

    # create specific datasource object
    ds = RegularImageStack(datapath)

    # call index 
    ds.index()

    self._datasources[datapath] = ds

