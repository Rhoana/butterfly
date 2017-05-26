# Get all the classes
from Datasource import Datasource
from TiffGrid import TiffGrid
from Mojo import Mojo
from HDF5 import HDF5

# Get all the derived classes
__all__ = ['TiffGrid', 'HDF5', 'Mojo']
# Get the base class
__all__ += ['Datasource']
