""" Provieds Keywords, Logging templates, and an argument handler.

Attributes
-----------
BFLY_CONFIG : dict
   Loads all data from  the rh-config given\
by the :mod:`rh_config` module.

"""
# Get all the constants
from Settings import BFLY_CONFIG
from Settings import MAX_CACHE_SIZE
from Settings import ALLOWED_PATHS
from Settings import DEV_MODE
from Settings import LOG_PATH
from Settings import DB_PATH
from Settings import DB_TYPE
from Settings import PORT

# Get all the classes
from Keywords import INPUT
from Keywords import RUNTIME
from Keywords import OUTPUT
from Argv import Argv

# Get the structure classes
from Structures import NamedStruct
from Structures import NamelessStruct

# Get a module for documentation
from . import rh_config

# Get a static method
to_argv = Argv.to_argv

# Define all the constants, classes, and methods in UtilityLayer
__all__ = ['PORT','DB_TYPE','DB_PATH','ALLOWED_PATHS','DEV_MODE']
__all__ += ['BFLY_CONFIG','to_argv','rh_config']
__all__ += ['NamedStruct','NamelessStruct']
__all__ += ['INPUT','RUNTIME','OUTPUT']
__all__ += ['BFLY_CONFIG']
