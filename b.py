#!/usr/bin/env python

import _butterfly
import cv2
import argparse

# Custom parsing of the args file
def convert_arg_line_to_args(arg_line):
    for arg in arg_line.split():
        if not arg.strip():
            continue
        yield arg

core = _butterfly.Core()

#Parser for command-line arguments - to be incorporated separately in a client-side tool
parser = argparse.ArgumentParser(description='Returns cutout of requested volume from a given EM stack', fromfile_prefix_chars='@', add_help=False)
parser.convert_arg_line_to_args = convert_arg_line_to_args

#Argument group for input/output paths
paths = parser.add_argument_group('Paths')
paths.add_argument('-h', '--help', action='help', help=argparse.SUPPRESS)
paths.add_argument('datapath', help='Path to EM stack')
paths.add_argument('--output', metavar='filename', help='Output file name (with extension), use sprintf format for multiple slices', required=True)

#Argument group for information about requested volume
v_inf = parser.add_argument_group('Requested volume')
v_inf.add_argument('--start', nargs=3, type=int, metavar=('X','Y','Z'), help='Starting coordinates of the requested volume', required=True)
v_inf.add_argument('--size', nargs=3, type=int, metavar=('X','Y','Z'), help='Size of the requested volume', required=True)
v_inf.add_argument('--zoom', nargs='?', type=int, default=0, metavar='level', help='MIP map level, 0 is default')

#Hidden argument group for parameters - temporary for now! Will not be on client, and will be optional on server
d_inf = parser.add_argument_group()
d_inf.add_argument('--filename', help=argparse.SUPPRESS, required=True) #EM stack filenames in sprintf format
d_inf.add_argument('--folderpaths', help=argparse.SUPPRESS, required=True) #Folder names for each vertical slice in sprintf format
d_inf.add_argument('--x_ind', nargs='+', type=int, help=argparse.SUPPRESS, required=True) #Row indices of the filenames
d_inf.add_argument('--y_ind', nargs='+', type=int, help=argparse.SUPPRESS, required=True) #Column indices of the filenames
d_inf.add_argument('--z_ind', nargs='+', type=int, help=argparse.SUPPRESS, required=True) #Slice indices of the filenames
d_inf.add_argument('--blocksize', nargs=2, type=int, help=argparse.SUPPRESS, required=True) #Tile size of each image (X, Y)

args = parser.parse_args()
#Paths and filenames for the current image set
datapath = args.datapath
# datapath = '/Volumes/DATA1/P3/'
# datapath = '/home/e/Documents/Data/P3/'

filename = args.filename
folderpaths = args.folderpaths

#Tile and slice index ranges
z_ind = args.z_ind
y_ind = args.y_ind
x_ind = args.x_ind
indices = (x_ind, y_ind, z_ind)

#Requested volume (coordinates are for the entire current image set)
start_coord = args.start
vol_size = args.size
zoom_level = args.zoom

#In the case of regular image stacks we manually input paths
core.create_datasource(datapath)
ris = core._datasources[datapath]
ris.load_paths(folderpaths, filename, indices)

#Temporary input of blocksize, should be able to grab from index in the future
ris.blocksize = args.blocksize

#Grab the sample volume
volume = core.get(datapath, start_coord, vol_size, zoom_level)

if vol_size[2] == 1:
	#Is there a better way to catch errors?
	try:
		cv2.imwrite(args.output, volume[:,:,0].astype('uint8'))
	except cv2.error as e:
		print 'Could not write image'
else:
	for i in range(vol_size[2]):
		try:
			cv2.imwrite(args.output % i, volume[:,:,i].astype('uint8'))
		except cv2.error as e:
			print 'Could not write image'

print volume.shape
