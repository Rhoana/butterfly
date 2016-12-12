import os
import glob
import h5py
import numpy as np
from rh_logger import logger
from datasource import DataSource

class Mojo(DataSource):

    def __init__(self, core, datapath):
        '''
        @override
        '''
        if not os.path.isdir(datapath) or 'tiles' not in os.listdir(datapath):
            raise IndexError("Datapath %s is not a Mojo data path" % datapath)
        super(Mojo, self).__init__(core, datapath)

    def index(self):
        '''
        @override
        '''
        folderpaths = 'z=%08d'

        # Max zoom level
        base_path = os.path.join(self._datapath, 'tiles')
        zoom_folders = os.path.join(base_path, 'w=*')
        self.max_zoom = len(glob.glob(zoom_folders)) - 1

        # Try first image to get extension
        tmp_file = os.path.join(
            base_path,
            'w=00000000',
            'z=00000000',
            'y=00000000,x=00000000.*')
        img_ext = os.path.splitext(glob.glob(tmp_file)[0])[1]
        filename = 'y=%(y)08d,x=%(x)08d' + img_ext

        # Tile and slice index ranges
        slice_folders = glob.glob(os.path.join(base_path, 'w=00000000', 'z=*'))
        y_tiles = os.path.join(slice_folders[0], 'y=*,x=00000000' + img_ext)
        x_tiles = os.path.join(slice_folders[0], 'y=00000000,x=*' + img_ext)
        num_slices = len(slice_folders)
        z_ind = range(num_slices)
        y_ind = range(len(glob.glob(y_tiles)))
        x_ind = range(len(glob.glob(x_tiles)))
        indices = (x_ind, y_ind, z_ind)

        # Load info
        self.load_info(folderpaths, filename, indices)

        # Grab blocksize from first image
        tmp_img = self.load(0, 0, 0, 0)
        # print 'Indexing complete.\n'
        self.blocksize = tmp_img.shape

        super(Mojo, self).index()

    def load_info(self, folderpaths, filename, indices):
        self._folderpaths = folderpaths
        self._filename = filename
        self._indices = indices

    def load(self, x, y, z, w, segmentation=False):
        '''
        @override
        '''

        cur_filename = self._filename % {
            'x': self._indices[0][x],
            'y': self._indices[1][y]
        }

        logger.report_event("Mojo loading " + cur_filename)

        if w <= self.max_zoom:
            cur_path = os.path.join(
                self._datapath,
                'tiles',
                'w=%08d' % w,
                self._folderpaths %
                self._indices[2][z],
                cur_filename)
            # We pass zero mip level to use the files on disk, as we don't need
            # .load() to resize
            return super(Mojo, self).load(cur_path, 0)

        cur_path = os.path.join(
            self._datapath,
            'tiles',
            'w=00000000',
            self._folderpaths %
            self._indices[2][z],
            cur_filename)
        return super(Mojo, self).load(cur_path, w, segmentation)

    def seg_to_color(self, slice):
        colors = np.zeros(slice.shape+(3,),dtype=np.uint8)
        colors[:,:,0] = np.mod(107*slice[:,:],700).astype(np.uint8)
        colors[:,:,1] = np.mod(509*slice[:,:],900).astype(np.uint8)
        colors[:,:,2] = np.mod(200*slice[:,:],777).astype(np.uint8)
        return colors

    def get_boundaries(self):
        # super(Mojo, self).get_boundaries()

        return (len(self._indices[0]) *
                self.blocksize[0], len(self._indices[1]) *
                self.blocksize[1], len(self._indices[2]))
