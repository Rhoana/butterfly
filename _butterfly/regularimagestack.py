import argparse
from datasource import Datasource
import os
import cv2

def convert_arg_line_to_args(arg_line):
    for arg in re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', arg_line):
        if not arg.strip():
            continue
        yield arg.strip('\'\"')

def parseNumRange(num_arg):
    match = re.match(r'(\d+)(?:-(\d+))?$', num_arg)
    if not match:
        raise argparse.ArgumentTypeError("'" + num_arg + "' must be a number or range (ex. '5' or '0-10').")
    start = match.group(1)
    end = match.group(2) or match.group(1)
    step = 1
    if end < start:
        step = -1
    return list(range(int(start), int(end) + step, step))


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

    d_inf = argparse.ArgumentParser(fromfile_prefix_chars='@')
    d_inf.convert_arg_line_to_args = convert_arg_line_to_args


    d_inf.add_argument('--filename', help=argparse.SUPPRESS, required=True) #EM stack filenames in sprintf format
    d_inf.add_argument('--folderpaths', help=argparse.SUPPRESS, required=True) #Folder names for each vertical slice in sprintf format
    d_inf.add_argument('--x_ind', nargs='+', type=parseNumRange, help=argparse.SUPPRESS, required=True) #Row indices of the filenames
    d_inf.add_argument('--y_ind', nargs='+', type=parseNumRange, help=argparse.SUPPRESS, required=True) #Column indices of the filenames
    d_inf.add_argument('--z_ind', nargs='+', type=parseNumRange, help=argparse.SUPPRESS, required=True) #Slice indices of the filenames
    d_inf.add_argument('--blocksize', nargs=2, type=int, help=argparse.SUPPRESS, required=True) #Tile size of each image (X, Y)

    args_file = os.path.join(self._datapath,'ac3.args')
    args = d_inf.parse_args('--filename %(z)04d_Tile_r1-c1_W02_sec%(z)03d_tr%(y)d-tc%(x)d_.png')#'@'+args_file)

    print args

    datapath = args.datapath
    # datapath = '/Volumes/DATA1/P3/'
    # datapath = '/home/e/Documents/Data/P3/'

    filename = args.filename
    folderpaths = args.folderpaths

    #Tile and slice index ranges - the list comprehensions can be understood as nested for loops to flatten list
    z_ind = [number for sublist in args.z_ind for number in sublist]
    y_ind = [number for sublist in args.y_ind for number in sublist]
    x_ind = [number for sublist in args.x_ind for number in sublist]
    indices = (x_ind, y_ind, z_ind)

    #Requested volume (coordinates are for the entire current image set)
    start_coord = args.start
    vol_size = args.size
    zoom_level = args.zoom

    #In the case of regular image stacks we manually input paths
    # core.create_datasource(datapath)
    ris = self#core._datasources[datapath]
    ris.load_paths(folderpaths, filename, indices)

    #Temporary input of blocksize, should be able to grab from index in the future
    ris.blocksize = args.blocksize    


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