from Datasource import Datasource
import numpy as np
import h5py

class HDF5(Datasource):
    pass
    @classmethod
    def load_tile(ds, query):
        Sk,Sj,Si = query.all_scales
        path = query.OUTPUT.INFO.PATH.VALUE
        (K0,J0,I0),(K1,J1,I1) = query.source_bounds

        with h5py.File(path) as fd:
            vol = fd[fd.keys()[0]]
            return vol[::Sk,::Sj,::Si]

