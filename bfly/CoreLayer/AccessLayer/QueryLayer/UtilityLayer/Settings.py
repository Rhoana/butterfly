from .rh_config import config_filename
from .rh_config import config
import os

# Server settings
BFLY_CONFIG = config.get("bfly", {})
CONFIG_FILENAME = config_filename

#HTTP port for server
PORT = int(BFLY_CONFIG.get("port", 2001))
#Path to database and kind of database
DB_PATH = BFLY_CONFIG.get("db-path", "bfly.db")
DB_TYPE = BFLY_CONFIG.get("db-type", "Unqlite")
#Path to the log file
LOG_PATH = BFLY_CONFIG.get("log-path", "bfly.log")

#Maximum size of the cache in MiB: 1 GiB by default
_max_cache = BFLY_CONFIG.get("max-cache-size", 1024)
MAX_CACHE_SIZE = int(_max_cache) * (1024**2)

#Paths must start with one of the following allowed paths
ALLOWED_PATHS = BFLY_CONFIG.get("allowed-paths", [os.sep])

