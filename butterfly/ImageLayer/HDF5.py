from Datasource import Datasource
import numpy as np
import h5py
import json
import os

class HDF5(Datasource):

    read = [json.load]
    meta_files = ['.json']

    @staticmethod
    def h5_info(query):
        path = query.OUTPUT.INFO.PATH
        h5_info = query.RUNTIME.IMAGE.SOURCE.HDF5
        return [path,h5_info.INNER]

    @staticmethod
    def load_tile(query):

        # call superclass
        Datasource.load_tile(query)
        # Load information about full hdf5
        path, inner = HDF5.h5_info(query)

        # Find the region to crop
        Sk,Sj,Si = query.all_scales
        z0,y0,x0 = query.tile_origin
        z1,y1,x1 = query.tile_origin + query.blocksize

        with h5py.File(path.VALUE) as fd:
            vol = fd[inner.VALUE]
            return vol[z0:z1:Sk,y0:y1:Sj,x0:x1:Si]

    @staticmethod
    def preload_source(query):
        # Keyword names
        output = query.OUTPUT.INFO
        runtime = query.RUNTIME.IMAGE
        inner = runtime.SOURCE.HDF5.INNER
        # call superclass
        Datasource.preload_source(query)

        # Check if path is valid
        keywords = HDF5.valid_path(query)
        if not keywords:
            return {}
        # Get validated name and dataset
        filename = keywords[output.PATH.NAME]
        dataset = keywords[inner.NAME]
        # Load properties from H5 dataset
        with h5py.File(filename,'r') as fd:
            vol = fd[dataset]
            block = (1,)+vol.shape[1:]
            # return named keywords
            keywords.update({
                output.TYPE.NAME: str(vol.dtype),
                runtime.BLOCK.NAME: np.uint32(block),
                output.SIZE.NAME: np.uint32(vol.shape)
            })
            return keywords

    @staticmethod
    def valid_path(query):
        # Dereference path to hdf5 data
        path, inner = HDF5.h5_info(query)
        filename, dataset = HDF5.load_info(query)
        # Try to load the file
        try:
            with h5py.File(filename,'r') as fd:
                if dataset not in fd.keys():
                    dataset = fd.keys()[0]
                return {
                    path.NAME: filename,
                    inner.NAME: dataset
                }
        except IOError:
            return False

    @staticmethod
    def load_info(query):
        # Load information about full hdf5
        h5_info = query.RUNTIME.IMAGE.SOURCE.HDF5
        filename = query.OUTPUT.INFO.PATH.VALUE
        dataset = h5_info.INNER.VALUE

        # Load path if ends with json
        ending = os.path.splitext(filename)[1]
        if ending in HDF5.meta_files:
            # Read the metainfo file
            order = HDF5.meta_files.index(ending)
            with open(filename) as infile:
                info = HDF5.read[order](infile)
                # Get the inner dataset and the new path
                filename = info[h5_info.OUTER.NAME]
                dataset = info[h5_info.INNER.NAME]

        return [filename, dataset]

