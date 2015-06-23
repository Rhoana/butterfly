#!/usr/bin/env python

import _butterfly

core = _butterfly.Core()

#Paths and filenames for the current image set
#datapath = '/Volumes/DATA1/P3/'
datapath = '/home/e/Documents/Data/P3/'
filename = '%(z)04d_Tile_r1-c1_W02_sec%(z)03d_tr%(y)d-tc%(x)d_.png'
folderpaths = '%(z)04d_Tile_r1-c1_W02_sec%(z)03d'

#Tile and slice index ranges
z_ind = range(1,4)
y_ind = range(1,5)
x_ind = range(1,4)
indices = (x_ind, y_ind, z_ind)

#Assume all images are of the same size - (x, y) coordinates
block_size = [16384, 16384]

#Requested volume (coordinates are for the entire current image set)
start_coord = [16000, 16000, 0]
vol_size = [1024, 1024, 2]

#In the case of regular image stacks we manually input paths
core.create_datasource(datapath)
ris = core._datasources[datapath]
ris.load_paths(folderpaths, filename, indices)

#Temporary input of blocksize
ris.blocksize = block_size

#Grab the sample volume
volume = core.get(datapath, start_coord, vol_size)
print(volume)
print volume.shape
