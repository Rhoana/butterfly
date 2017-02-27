from Datasource import Datasource
import numpy as np
import h5py

class HDF5(Datasource):
    pass
    @classmethod
    def load_tile(ds, query):
        Sk,Sj,Si = query.all_scales
        path = query.OUTPUT.INFO.PATH.VALUE
        z0,y0,x0 = query.index_zyx*query.blocksize
        z1,y1,x1 = query.index_zyx*query.blocksize + query.blocksize

        with h5py.File(path) as fd:
            vol = fd[fd.keys()[0]]
            return vol[z0:z1:Sk,y0:y1:Sj,x0:x1:Si]

