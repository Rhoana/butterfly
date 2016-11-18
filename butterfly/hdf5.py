'''An HDF5 data source'''

import os
import h5py
import json
import logging
from rh_logger import logger
import numpy as np
import settings

from .datasource import DataSource

'''The JSON dictionary key for layer channel type'''
K_CHANNEL = 'channel'

'''The JSON dictionary key for the filename (including path) of the HDF5 file'''
K_FILENAME = 'filename'

'''The JSON dictionary key of the path to the dataset inside the HDF5 file'''
K_DATASET_PATH = 'dataset-path'

'''The default filenames data if no JSON file'''
K_PRESET_FILENAMES = ['image.h5','segmentation.h5','synapse.h5']

'''The default channels by array index if not in JSON file'''
K_PRESET_CHANNELS = ['img','seg','syn']

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
        layers = self.defaultLayers(datapath)
        if not layers:
            warn = "HDF5 path %s must point to valid h5" % datapath
            raise IndexError(warn)
        self.channels = self.storeChannels(layers)
        self.kinds = list(self.channels.keys())
        super(HDF5DataSource, self).__init__(core, datapath)

    def defaultLayers(self,path):
        layers = []
        if path.endswith('.json'):
            layers = json.load(open(path, "r"))
            if type(layers) is not list:
                layers = [layers]
        elif os.path.isdir(path):
            h5files = [i for i in os.listdir(path) if i.endswith('.h5')]
            if h5files:
                for name, kind in zip(K_PRESET_FILENAMES,K_PRESET_CHANNELS):
                    if name in h5files:
                        fullName = os.path.join(path,name)
                        with h5py.File(fullName, "r") as fd:
                            layer = dict([(K_FILENAME, fullName)])
                            layer[K_DATASET_PATH] = fd.keys()[0]
                            layer[K_CHANNEL] = kind
                            layers.append(layer)
        return layers

    def kindGuess(self,id):
        return K_PRESET_CHANNELS[int(id)%len(K_PRESET_CHANNELS)]

    def storeChannels(self,layers):
        channels = {}
        for lid,layer in enumerate(layers):
            if K_CHANNEL not in layer:
                layer[K_CHANNEL] = self.kindGuess(lid)
            channels[layer[K_CHANNEL]] = layer
        return channels

    def index(self):
        '''
        @override
        '''
        firstChannel = self.channels[self.kinds[0]]
        with h5py.File(firstChannel[K_FILENAME], "r") as fd:
            self.blocksize = fd[firstChannel[K_DATASET_PATH]].shape[-1:0:-1]
        return

    def load_cutout(self, x0, x1, y0, y1, z, w):
        '''
        @override
        '''
        channelKind = self.kindGuess(0)
        if channelKind not in self.kinds:
            return 0
        channel = self.channels[channelKind]
        with h5py.File(channel[K_FILENAME], "r") as fd:
            ds = fd[channel[K_DATASET_PATH]]
            return ds[z, y0:y1:(2 ** w), x0:x1:(2 ** w)]

    def load(self, x, y, z, w, segmentation):
        '''
        @override
        '''
        channelKind = self.kindGuess(segmentation)
        if channelKind not in self.kinds:
            return 0
        channel = self.channels[channelKind]
        with h5py.File(channel[K_FILENAME], "r") as fd:
            (bx,by) = self.blocksize
            ds = fd[channel[K_DATASET_PATH]]
            return ds[z, y:y+by:(2 ** w), x:x+bx:(2 ** w)]

    def seg_to_color(self, slice):
        colors = np.zeros(slice.shape+(3,),dtype=np.uint8)
        colors[:,:,0] = np.mod(107*slice[:,:],700).astype(np.uint8)
        colors[:,:,1] = np.mod(509*slice[:,:],900).astype(np.uint8)
        colors[:,:,2] = np.mod(200*slice[:,:],777).astype(np.uint8)
        return colors

    def get_boundaries(self):
        firstChannel = self.channels[self.kinds[0]]
        with h5py.File(firstChannel[K_FILENAME], "r") as fd:
            return fd[firstChannel[K_DATASET_PATH]].shape[::-1]

    def get_dataset(self,path):
        dataset = {'name':os.path.basename(path),'channels':[]}
        dimensions = dict(zip(('x','y','z'),self.get_boundaries()))
        for kind,channel in self.channels.iteritems():
            innerPath = channel[K_DATASET_PATH]
            base = os.path.splitext(os.path.basename(channel[K_FILENAME]))[0]
            base += ' '+os.path.basename(innerPath)
            subset = {'path':path,'dimensions':dimensions,'name':base}
            with h5py.File(channel[K_FILENAME], "r") as fd:
                subset['data-type'] = fd[innerPath].dtype.name
            dataset['channels'].append(subset)
        return dataset
