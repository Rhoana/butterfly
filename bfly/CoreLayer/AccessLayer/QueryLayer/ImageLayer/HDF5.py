from Datasource import Datasource
import numpy as np
import h5py
import json
import os

class HDF5(Datasource):

    read = [json.load]
    meta_files = ['.json']

    @staticmethod
    def load_tile(query):

        # call superclass
        Datasource.load_tile(query)
        # Load information about full hdf5
        h5_info = query.RUNTIME.IMAGE.SOURCE.HDF5

        # Find the region to crop
        sk,sj,si = query.all_scales
        z0,y0,x0 = query.tile_origin
        z1,y1,x1 = query.tile_origin + query.blocksize

        with h5py.File(h5_info.OUTER.VALUE) as fd:
            vol = fd[h5_info.INNER.VALUE]
            return vol[z0:z1:sk,y0:y1:sj,x0:x1:si]

    @staticmethod
    def preload_source(query):
        # Keyword names
        output = query.OUTPUT.INFO
        runtime = query.RUNTIME.IMAGE
        h5_info = runtime.SOURCE.HDF5
        # call superclass
        Datasource.preload_source(query)

        # Check if path is valid
        keywords = HDF5.valid_path(query)
        if not keywords:
            return keywords

        # Get validated name and dataset
        filename = keywords[h5_info.OUTER.NAME]
        dataset = keywords[h5_info.INNER.NAME]
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
        # Return all canonical keywords
        return keywords

    @staticmethod
    def valid_path(query):
        # Dereference path to hdf5 data
        h5_info = query.RUNTIME.IMAGE.SOURCE.HDF5
        filename, dataset = HDF5.load_info(query)
        # Try to load the file
        try:
            with h5py.File(filename,'r') as fd:
                if dataset not in fd.keys():
                    dataset = fd.keys()[0]
                return {
                    h5_info.OUTER.NAME: filename,
                    h5_info.INNER.NAME: dataset
                }
        except IOError:
            return {}

    @staticmethod
    def load_info(query):
        # Load information about full hdf5
        h5_info = query.RUNTIME.IMAGE.SOURCE.HDF5
        filename = query.OUTPUT.INFO.PATH.VALUE
        dataset = h5_info.INNER.VALUE

        # Load path if ends with json
        ending = os.path.splitext(filename)[1]
        if ending in HDF5.meta_files:
            # Get function to read the metainfo file
            order = HDF5.meta_files.index(ending)
            try:
                with open(filename) as infile:
                    # Read the metainfo file
                    info = HDF5.read[order](infile)
            except IOError:
                return [filename, dataset]
            # Get the inner dataset and the new path
            filename = info[h5_info.OUTER.NAME]
            dataset = info[h5_info.INNER.NAME]

        return [filename, dataset]

