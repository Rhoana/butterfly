'''An HDF5 data source'''

import h5py
import json
import numpy as np
import settings

from .datasource import DataSource

'''The JSON dictionary key for the filename (including path) of the HDF5 file'''
K_FILENAME = 'filename'

'''The JSON dictionary key of the path to the dataset inside the HDF5 file'''
K_DATASET_PATH = 'dataset-path'

class HDF5DataSource(DataSource):
    '''An HDF5 data source
    
    An HDF5 data source consists of a .json file that contains a dictionary
    with the following keys:
    
    filename: the name of the HDF5 file
    dataset-path: the path inside the HDF5 file to the dataset
    
    The dataset may be sparse (with zero for areas w/o data) so the coordinate
    system is implicit, starting at 0, 0, 0.
    '''
    
    def __init__(self, core, datapath, dtype=np.uint8):
        layers = json.load(open(datapath, "r"))
        if type(layers) is not list:
            layers = [layers]
        self.layers = len(layers)
        self.hdf5_file = [d[K_FILENAME] for d in layers]
        self.data_path = [d[K_DATASET_PATH] for d in layers]
        super(HDF5DataSource, self).__init__(core, datapath)
    
    def index(self):
        with h5py.File(self.hdf5_file[0], "r") as fd:
            self.blocksize = fd[self.data_path[0]].shape[1:]
        return
    
    def load_cutout(self, x0, x1, y0, y1, z, w):
        with h5py.File(self.hdf5_file[0], "r") as fd:
            ds = fd[self.data_path[0]]
            stride = 2 ** w
            return ds[z, y0:y1:stride, x0:x1:stride]

    def load(self, x, y, z, w, segmentation):
        layerIndex = int(segmentation)%self.layers
        with h5py.File(self.hdf5_file[layerIndex], "r") as fd:
            stride = 2 ** w
            ds = fd[self.data_path[layerIndex]]
            (bx,by) = self.blocksize
            return ds[z, y:y+by:stride, x:x+bx:stride]

    def seg_to_color(self, slice):
        # Simply expand all 32 bit ids into four 8 bit ints
        slice = slice.astype(np.uint32)
        colors = slice.view(np.uint8).reshape(slice.shape + (4,))
        return colors[:,:,:3]
    
    def get_boundaries(self):
        with h5py.File(self.hdf5_file[0], "r") as fd:
            ds = fd[self.data_path[0]]
            return (ds.shape[2], ds.shape[1], ds.shape[0])
