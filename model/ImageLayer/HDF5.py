from Datasource import Datasource
import numpy as np

class HDF5(Datasource):
    pass

    def load_tile(self, query):
        Z = query.XYZ[-1]
        S,I,J = query.SIJ
        fake_h5 = np.zeros([64,4096,16384],dtype=np.uint8)
        return fake_h5[Z, J[0]:J[1]:S, I[0]:I[1]:S]

