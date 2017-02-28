from Datasource import Datasource
import numpy as np
import h5py

class HDF5(Datasource):

    @staticmethod
    def load_tile(query):

        # call superclass
        Datasource.load_tile(query)

        Sk,Sj,Si = query.all_scales
        path = query.OUTPUT.INFO.PATH.VALUE
        z0,y0,x0 = query.index_zyx*query.blocksize
        z1,y1,x1 = query.index_zyx*query.blocksize + query.blocksize

        with h5py.File(path) as fd:
            vol = fd[fd.keys()[0]]
            return vol[z0:z1:Sk,y0:y1:Sj,x0:x1:Si]

    @staticmethod
    def preload_source(query):

        # call superclass
        Datasource.preload_source(query)
        # Load information about full hdf5
        path = query.OUTPUT.INFO.PATH.VALUE
        with h5py.File(path) as fd:
            vol = fd[fd.keys()[0]]
            block = (1,)+vol.shape[1:]
            # return named keywords
            output = query.OUTPUT.INFO
            runtime = query.RUNTIME.IMAGE
            return {
                output.TYPE.NAME: str(vol.dtype),
                runtime.BLOCK.NAME: np.uint32(block),
                output.SIZE.NAME: np.uint32(vol.shape)
            }
