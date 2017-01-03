import argparse
from datasource import DataSource
import os
import re
import glob


def convert_arg_line_to_args(arg_line):
    for arg in re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', arg_line):
        if not arg.strip():
            continue
        yield arg.strip('\'\"\n')


def parseNumRange(num_arg):
    match = re.match(r'(\d+)(?:-(\d+))?$', num_arg)
    if not match:
        raise argparse.ArgumentTypeError(
            "'" + num_arg + "' must be a number or range (ex. '5' or '0-10').")
    start = match.group(1)
    end = match.group(2) or match.group(1)
    step = 1
    if end < start:
        step = -1
    return list(range(int(start), int(end) + step, step))


class RegularImageStack(DataSource):

    def __init__(self, core, datapath):
        '''
        @override
        '''

        super(RegularImageStack, self).__init__(core, datapath)

    def index(self):
        '''
        @override
        '''

        args_file = os.path.join(self._datapath, '*.args')
        args_file = glob.glob(args_file)[0]

        with open(args_file, 'r') as f:
            args_list = [
                arg for line in f for arg in convert_arg_line_to_args(line)]

        args = d_inf.parse_args(args_list)
        filename = args.filename
        folderpaths = args.folderpaths
        # blocksize = args.blocksize

        # Tile and slice index ranges - the list comprehensions can be
        # understood as nested for loops to flatten list
        z_ind = [number for sublist in args.z_ind for number in sublist]
        y_ind = [number for sublist in args.y_ind for number in sublist]
        x_ind = [number for sublist in args.x_ind for number in sublist]
        indices = (x_ind, y_ind, z_ind)

        # Load info from args file
        self.load_info(folderpaths, filename, indices)

        # Grab blocksize from first image
        self.blocksize = self.get_blocksize()

        super(RegularImageStack, self).index()

    def load_info(self, folderpaths, filename, indices):
        self._folderpaths = folderpaths
        self._filename = filename
        self._indices = indices

    def get_blocksize(self):
        tmp_img = self.load(self._indices[0][0], self._indices[1][0], 0, 0)
        return tmp_img.shape

    def load(self, x, y, z, w):
        '''
        @override
        '''

        cur_filename = self._filename % {
            'x': self._indices[0][x],
            'y': self._indices[1][y],
            'z': self._indices[2][z]}
        print '\n'
        print cur_filename
        cur_path = os.path.join(
            self._datapath,
            self._folderpaths % {
                'z': self._indices[2][z]},
            cur_filename)
        return super(RegularImageStack, self).load(cur_path, w)

    def get_boundaries(self):
        # super(RegularImageStack, self).get_boundaries()

        return (len(self._indices[0]) *
                self.blocksize[0], len(self._indices[1]) *
                self.blocksize[1], len(self._indices[2]))
