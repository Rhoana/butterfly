'''An HDF5 data source'''

import os
import h5py
import json
import logging
from rh_logger import logger
import numpy as np
import settings

from .datasource import DataSource

'''The JSON dictionary key for the filename (including path) of the HDF5 file'''
K_FILENAME = 'filename'

'''The JSON dictionary key of the path to the dataset inside the HDF5 file'''
K_DATASET_PATH = 'dataset-path'

'''The JSON dictionary key for the Z offset of the volume'''
K_Z_OFFSET = 'z-offset'

K_DEPTH = 'depth'

K_DTYPE = 'dtype'

class HDF5DataSource(DataSource):
    '''An HDF5 data source

    An HDF5 data source consists of a .json file that contains a dictionary
    or a list of dictionaries with the following keys:

    filename: the name of the HDF5 file
    dataset-path: the path inside the HDF5 file to the dataset
    z-offset (optional): the z offset of the volume (default = 0)

    The dataset may be sparse (with zero for areas w/o data) so the coordinate
    system is implicit, starting at 0, 0, 0.
    '''

    def __init__(self, core, datapath, dtype=np.uint8):
        self._dataset = self.loadFolder(datapath)
        if not self._dataset:
            warn = "HDF5 path %s must point to valid h5" % datapath
            raise IndexError(warn)
        super(HDF5DataSource, self).__init__(core, datapath)

    def loadFolder(self,path):
        if path.endswith('.json'):
            result = json.load(open(path, "r"))
            if isinstance(result, dict):
                result = [result]
            for d in result:
                if K_Z_OFFSET not in d:
                    d[K_Z_OFFSET] = 0
                with h5py.File(d[K_FILENAME]) as fd:
                    d[K_DEPTH] = fd[d[K_DATASET_PATH]].shape[0]
                    self._dtype = fd[d[K_DATASET_PATH]].dtype
            return result

        elif path.endswith('.h5'):
            with h5py.File(path, "r") as fd:
                key0 = fd.keys()[0]
                self._dtype = fd[key0].dtype
                return [{
                    K_FILENAME : path,
                    K_DATASET_PATH : key0,
                    K_DEPTH: fd[key0].shape[0],
                    K_Z_OFFSET: 0,
                }]
        else:
            return False

    def index(self):
        '''
        @override
        '''
        with h5py.File(self._dataset[0][K_FILENAME], "r") as fd:
            dataset = fd[self._dataset[0][K_DATASET_PATH]]
            self.blocksize = dataset.shape[1:][::-1]

        super(HDF5DataSource, self).index()

    def get_plane_info(self, z):
        '''Get the filename, dataset path and z-index for a given plane

        :param z: plane #
        :returns: a tuple of HDF5 filename, dataset name and z index or 
                  (None, None, None) if no HDF5 file is within range
        '''
        for d in self._dataset:
            z_offset = d[K_Z_OFFSET]
            depth = d[K_DEPTH]
            if z_offset <= z and z_offset+depth > z:
                return d[K_FILENAME], d[K_DATASET_PATH], z-z_offset
        return (None, None, None)

    def load_cutout(self, x0, x1, y0, y1, z, w):
        '''
        @override
        '''
        filename, dataset_path, z_idx = self.get_plane_info(z)
        if filename is None:
            return np.zeros(((y1 - y0) / (2 ** w),
                             (x1-x0) / (2**w)), dtype=self._dtype)

        with h5py.File(filename, "r") as fd:
            ds = fd[dataset_path]
            if ds.shape[1] < y1 or ds.shape[2] < x1:
                result = np.zeros(((y1 - y0) / (2 ** w),
                                   (x1-x0) / (2**w)), dtype=self._dtype)
                cutout = ds[z_idx, y0:y1:(2 ** w), x0:x1:(2 ** w)]
                result[:cutout.shape[0], :cutout.shape[1]] = cutout
                return result
            return ds[z_idx, y0:y1:(2 ** w), x0:x1:(2 ** w)]

    def load(self, x, y, z, w, segmentation=False):
        '''
        @override
        '''
        (bx,by) = self.blocksize
        filename, dataset_path, z_idx = self.get_plane_info(z)
        if filename is None:
            return np.zeros((by / (2 ** w),
                             bx / (2**w)), dtype=self._dtype)

        with h5py.File(filename, "r") as fd:
            dataset = fd[dataset_path]
            return dataset[z, y:y+by:(2 ** w), x:x+bx:(2 ** w)]

    def seg_to_color(self, slice):
        colors = np.zeros(slice.shape+(3,),dtype=np.uint8)
        colors[:,:,0] = np.mod(107*slice[:,:],700).astype(np.uint8)
        colors[:,:,1] = np.mod(509*slice[:,:],900).astype(np.uint8)
        colors[:,:,2] = np.mod(200*slice[:,:],777).astype(np.uint8)
        return colors

    def get_boundaries(self):
        with h5py.File(self._dataset[K_FILENAME], "r") as fd:
            dataset = fd[self._dataset[K_DATASET_PATH]]
            self.blocksize = dataset.shape[::-1]
        return self.blocksize
