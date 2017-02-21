from rh_config import config
import cv2
import os

# Server settings
BFLY_CONFIG = config.get("bfly", {})

#HTTP port for server
PORT = int(BFLY_CONFIG.get("port", 2001))

#Maximum size of the cache in MiB: 1 GiB by default
_max_cache = BFLY_CONFIG.get("max-cache-size", 1024)
MAX_CACHE_SIZE = int(_max_cache) * (1024**2)

#Paths must start with one of the following allowed paths
ALLOWED_PATHS = BFLY_CONFIG.get("allowed-paths", [os.sep])

