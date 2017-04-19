""" Loads Settings from :mod:`UtilityLayer.rh_config`

Attributes
-------------
LOG_PATH : int
    Write logs to bfly.log or 'log-path' from :data:`config`
DB_TYPE : int
    Use Unqlite database or 'db-type' from :data:`config`
DB_PATH : int
    Write data to bfly.db or 'db-path' from :data:`config`
PORT : int
    Serve on 2001 or 'port' from :data:`config`
MAX_CACHE_SIZE : int
    Cache 1024^3 bytes or 1024^2 times 'max-cache-size'\
in megabytes from :data:`config`
BFLY_CONFIG : dict
    Values from 'bfly' key of :data:`config`
config : dict
    From :data:`UtilityLayer.rh_config.config`
config_filename : str
    From :data:`UtilityLayer.rh_config.config_filename`
"""


from .rh_config import config_filename
from .rh_config import config
import os

# Assent function
def is_yes(val):
    yes_list = ['y','true','yes','1']
    # Return whether the string matches
    return str(val).lower() in yes_list

# Get all server settings
BFLY_CONFIG = config.get('bfly', {})
CONFIG_FILENAME = config_filename

# HTTP port for server
PORT = int(BFLY_CONFIG.get('port', 2001))
# Path to database and kind of database
DB_PATH = BFLY_CONFIG.get('db-path', 'bfly.db')
DB_TYPE = BFLY_CONFIG.get('db-type', 'ZODB')
# Path to the log file
LOG_PATH = BFLY_CONFIG.get('log-path', 'bfly.log')

# Maximum size of the cache in MiB: 1 GiB by default
_max_cache = BFLY_CONFIG.get('max-cache-size', 1024)
MAX_CACHE_SIZE = int(_max_cache) * (1024**2)
# Maximum size of a single block in MiB: 1 MiB by default
_max_block = BFLY_CONFIG.get('max-block-size', 1)
MAX_BLOCK_SIZE = int(_max_block) * (1024**2)

# Paths must start with one of the following allowed paths
ALLOWED_PATHS = BFLY_CONFIG.get('allowed-paths', [os.sep])

# Whether to restart server on changed source-code
DEV_MODE = BFLY_CONFIG.get('developer-mode')
