import os
import numpy as np

import settings
from regularimagestack import RegularImageStack
from collections import OrderedDict
from mojo import Mojo


class Core(object):

    def __init__(self):
        '''
        '''
        self._datasources = {}
        self.vol_xy_start = [0, 0]
        self.tile_xy_start = [0, 0]
        self._cache = OrderedDict()
        self._max_cache_size = settings.MAX_CACHE_SIZE
        self._current_cache_size = 0

    def get(
            self,
            datapath,
            start_coord,
            vol_size,
            segmentation=False,
            segcolor=False,
            fit=False,
            w=0):
        '''
        Request a subvolume of the datapath at a given zoomlevel.
        '''

        # if datapath is not indexed (knowing the meta information like width,
        # height),do it now
        if datapath not in self._datasources:
            self.create_datasource(datapath)

        datasource = self._datasources[datapath]

        print 'Loading tiles:'

        # If the datasource has zoom levels already, we assume their tiles are
        # the same size across zooms
        f = w
        if w <= datasource.max_zoom:
            f = 0

        blocksize = [x // (2**f) for x in datasource.blocksize]

        # If we need to fit the volume to existing data, calculate volume size
        # now
        if fit:
            boundaries = datasource.get_boundaries()
            # No mip zoom for slices right now
            boundaries = [boundaries[0] //
                          (2**w), boundaries[1] //
                          (2**w), boundaries[2]]
            for i in range(3):
                if start_coord[i] + vol_size[i] > boundaries[i]:
                    vol_size[i] = boundaries[i] - start_coord[i]

        # Use 4D volume for rgb data, currently segmentation color is the only
        # use for color
        color = segcolor and segmentation
        if color:
            vol = np.zeros(
                (vol_size[1],
                 vol_size[0],
                    vol_size[2],
                    3),
                dtype=np.uint16)
        else:
            vol = np.zeros(
                (vol_size[1],
                 vol_size[0],
                    vol_size[2]),
                dtype=np.uint8)

        # Loop through all z-slices requested, using x,y offsets to calculate
        # distance until next block or volume end
        for z in range(vol_size[2]):
            # Calculate list of tiles that we need
            x_tiles = range(
                (start_coord[0] // blocksize[0]),
                (((start_coord[0] + vol_size[0] - 1) // blocksize[0]) + 1))
            y_tiles = range(
                (start_coord[1] // blocksize[1]),
                (((start_coord[1] + vol_size[1] - 1) // blocksize[1]) + 1))

            # Reset the x-starting coordinate for the next row of calculations
            self.vol_xy_start[0] = 0
            self.tile_xy_start[0] = (start_coord[0] % blocksize[0])
            for x in x_tiles:
                x_offset = min(
                    (blocksize[0] - self.tile_xy_start[0]),
                    (vol_size[0] - self.vol_xy_start[0]))

                # Reset the y-starting coordinate for the next column of areas
                self.vol_xy_start[1] = 0
                self.tile_xy_start[1] = (start_coord[1] % blocksize[1])

                for y in y_tiles:
                    y_offset = min(
                        (blocksize[1] - self.tile_xy_start[1]),
                        (vol_size[1] - self.vol_xy_start[1]))
                    try:
                        cur_img = datasource.load(
                            x, y, z + start_coord[2], w, segmentation)
                    except (IndexError, IOError, AttributeError):
                        cur_img = np.zeros(blocksize, dtype=np.uint8)

                    if color:
                        cur_img = datasource.seg_to_color(cur_img)

                    # Debug code to show which cutouts we are grabbing and from
                    # where
                    print 'tile:       ' + '(' + str(x) + ', ' + str(y) + ')'
                    # print 'z slice:    ' + str(z + start_coord[2])
                    # print 'vol start:  ' + str(self.vol_xy_start)
                    # print 'tile start: ' + str(self.tile_xy_start)
                    # print 'x offset:   ' + str(x_offset)
                    # print 'y offset:   ' + str(y_offset) + '\n'

                    # Add offsets in current y direction
                    target_boundaries = (
                        self.vol_xy_start[1],
                        self.vol_xy_start[1] +
                        y_offset,
                        self.vol_xy_start[0],
                        self.vol_xy_start[0] +
                        x_offset,
                        z)
                    source_boundaries = (
                        self.tile_xy_start[1],
                        self.tile_xy_start[1] + y_offset,
                        self.tile_xy_start[0],
                        self.tile_xy_start[0] + x_offset)

                    # print cur_img
                    print cur_img.shape
                    print 'Current cache size', self._current_cache_size

                    if color:
                        data = cur_img[
                            source_boundaries[0]:source_boundaries[1],
                            source_boundaries[2]:source_boundaries[3], :]
                        vol[target_boundaries[0]:target_boundaries[1],
                            target_boundaries[2]:target_boundaries[3],
                            target_boundaries[4], :] = data
                    else:
                        data = cur_img[
                            source_boundaries[0]:source_boundaries[1],
                            source_boundaries[2]:source_boundaries[3]]
                        vol[target_boundaries[0]:target_boundaries[1],
                            target_boundaries[2]:target_boundaries[3],
                            target_boundaries[4]] = data

                    self.tile_xy_start[1] = (
                        self.tile_xy_start[1] + y_offset) % blocksize[1]
                    self.vol_xy_start[1] += y_offset

                # Add offsets in current x direction
                self.tile_xy_start[0] = (
                    self.tile_xy_start[0] + x_offset) % blocksize[0]
                self.vol_xy_start[0] += x_offset

        return vol

    def create_datasource(self, datapath):
        '''
        '''

        # detect data source type
        last_folder = datapath.rstrip(os.sep).split(os.sep)[-1]
        last_folder = last_folder.lower()
        if last_folder == 'mojo':
            ds = Mojo(self, datapath)
        else:
            ds = RegularImageStack(self, datapath)

        # call index
        ds.index()

        self._datasources[datapath] = ds
