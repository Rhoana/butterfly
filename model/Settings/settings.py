from rh_config import config
import cv2
import os

bfly_config = config.get("bfly", {})
# Server settings

'''HTTP port for server'''
PORT = int(bfly_config.get("port", 2001))

'''Maximum size of the cache in MiB: 1 GiB by default'''
_max_cache = bfly_config.get("max-cache-size", 1024)
MAX_CACHE_SIZE = int(_max_cache) * (1024**2)

'''Queries that will enable flags'''
ASSENT_LIST = bfly_config.get("assent-list", ('yes', 'y', 'true'))

# Output settings
DEFAULT_OUTPUT = 'png'
DEFAULT_VIEW = 'grayscale'
# Using cv2 - please check if supported before adding!
SUPPORTED_IMAGE_FORMATS = ('png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp', 'zip')
SUPPORTED_IMAGE_VIEWS = ('grayscale','colormap','rgb')

'''List of datasources to try, in order, given a path'''
_datasources = ["hdf5", "tilespecs", "mojo", "regularimagestack"]
DATASOURCES = bfly_config.get("datasource", _datasources)

'''Paths must start with one of the following allowed paths'''
ALLOWED_PATHS = bfly_config.get("allowed-paths", [os.sep])

all = [SUPPORTED_IMAGE_FORMATS, SUPPORTED_IMAGE_VIEWS]
all = all + [ALLOWED_PATHS, DATASOURCES, ASSENT_LIST]
all = all + [DEFAULT_VIEW, DEFAULT_OUTPUT]
all = all + [MAX_CACHE_SIZE, PORT]
