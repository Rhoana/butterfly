from datasource import DataSource
import os
import cv2
import glob
import h5py
import numpy as np
import settings

class Mojo(DataSource):
  
    def __init__(self, core, datapath):
        '''
        @override
        '''

        super(Mojo, self).__init__(core, datapath)

    def index(self):
        '''
        @override
        '''

        super(Mojo, self).index()

        folderpaths = 'z=%08d'

        #Max zoom level
        base_path = os.path.join(self._datapath, 'images', 'tiles')
        base_ids_path = os.path.join(self._datapath, 'ids', 'tiles')
        zoom_folders = os.path.join(base_path, 'w=*')
        self.max_zoom = len(glob.glob(zoom_folders)) - 1 #Max zoom level

        #Segmentation ids
        ids_filename = 'y=%(y)08d,x=%(x)08d.hdf5'

        #Try first image to get extension
        tmp_file = os.path.join(base_path, 'w=00000000', 'z=00000000', 'y=00000000,x=00000000.*')
        img_ext = os.path.splitext(glob.glob(tmp_file)[0])[1]
        filename = 'y=%(y)08d,x=%(x)08d' + img_ext

        #Tile and slice index ranges
        slice_folders = glob.glob(os.path.join(base_path, 'w=00000000', 'z=*'))
        y_tiles = os.path.join(slice_folders[0], 'y=*,x=00000000' + img_ext)
        x_tiles = os.path.join(slice_folders[0], 'y=00000000,x=*' + img_ext)
        num_slices = len(slice_folders)
        z_ind = range(num_slices)
        y_ind = range(len(glob.glob(y_tiles)))
        x_ind = range(len(glob.glob(x_tiles)))
        indices = (x_ind, y_ind, z_ind)

        #Load info
        self.load_info(folderpaths, filename, ids_filename, indices)

        #Grab blocksize from first image
        tmp_img = self.load(0, 0, 0, 0)
        # print 'Indexing complete.\n'
        self.blocksize = tmp_img.shape

        #Grab color map
        color_map_path = glob.glob(os.path.join(self._datapath, 'ids', 'color*.hdf5'))
        if color_map_path:
            with h5py.File(color_map_path[0], 'r') as f:
                datasets = []
                f.visit(datasets.append)
                self._color_map = f[datasets[0]][()]

    def load_info(self, folderpaths, filename, ids_filename, indices):
        self._folderpaths = folderpaths
        self._filename = filename
        self._ids_filename = ids_filename
        self._indices = indices

    def load(self, x, y, z, w, segmentation=False):
        '''
        @override
        '''

        #Check for segmentation request
        if segmentation:
            cur_filename = self._ids_filename % {'x': self._indices[0][x], 'y': self._indices[1][y]}
            image_or_id = 'ids'
        else:
            cur_filename = self._filename % {'x': self._indices[0][x], 'y': self._indices[1][y]}
            image_or_id = 'images'

        print '\n'
        print cur_filename

        if w <= self.max_zoom:
            cur_path = os.path.join(self._datapath, image_or_id, 'tiles', 'w=%08d' % w, self._folderpaths % self._indices[2][z], cur_filename)
            #We pass zero mip level to use the files on disk, as we don't need .load() to resize
            return super(Mojo, self).load(cur_path, 0)

        cur_path = os.path.join(self._datapath, image_or_id, 'tiles', 'w=00000000', self._folderpaths % self._indices[2][z], cur_filename)
        return super(Mojo, self).load(cur_path, w, segmentation)

    def seg_to_color(self, slice):
        # super(Mojo, self).seg_to_color()

        #Modulo by length of color map, then advanced indexing to return rgb image
        return self._color_map[np.fmod(slice, len(self._color_map))]

    def get_boundaries(self):
        # super(Mojo, self).get_boundaries()

        return (len(self._indices[0])*self.blocksize[0], len(self._indices[1])*self.blocksize[1], len(self._indices[2]))
