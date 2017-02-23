from Datasource import Datasource
import numpy as np
import h5py

class HDF5(Datasource):
    pass
    @classmethod
    def load_tile(ds, query):
        Sk,Sj,Si = query.all_scales
        path = query.OUTPUT.INFO.PATH.VALUE
        (Zk0,Zk1),(Yj0,Yj1),(Xi0,Xi1) = query.full_coords

        with h5py.File(path) as fd:
            vol = fd[fd.keys()[0]]
            return vol[Zk0:Zk1:Sk,Yj0:Yj1:Sj,Xi0:Xi1:Si]

