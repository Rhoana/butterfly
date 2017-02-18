from Datasource import Datasource
import numpy as np
import h5py

class HDF5(Datasource):
    pass

    def load_tile(self, query):
        Z = query.index_xyz[-1]
        S,I,J = query.pixels_sij
        path = query.getatt('PATH')
        with h5py.File(path) as fd:
            volume = fd[fd.keys()[0]]
            return volume[Z, J[0]:J[1]:S, I[0]:I[1]:S]

