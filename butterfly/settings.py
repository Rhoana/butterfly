import cv2
import rh_config
import os

bfly_config = rh_config.config.get("bfly", {})
# Server settings

'''HTTP port for server'''
PORT = int(bfly_config.get("port", 2001))

'''Maximum size of the cache: 1G by default'''
MAX_CACHE_SIZE = int(bfly_config.get("max-cache-size", 1024)) * 1024 * 1024

'''Queries that will enable flags'''
ASSENT_LIST = bfly_config.get("assent-list", ('yes', 'y', 'true'))

ALWAYS_SUBSAMPLE = bool(bfly_config.get("always-subsample", True))
_image_resize_method = bfly_config.get("image-resize-method", "linear")

'''Interpolation method to use upon resizing'''
IMAGE_RESIZE_METHOD = \
    cv2.INTER_AREA if _image_resize_method == "area" else \
    cv2.INTER_CUBIC if _image_resize_method == "cubic" else \
    cv2.INTER_NEAREST if _image_resize_method == "nearest" else \
    cv2.INTER_LINEAR

# Output settings
DEFAULT_OUTPUT = '.png'
DEFAULTVIEW = 'grayscale'
# Using cv2 - please check if supported before adding!
SUPPORTED_IMAGE_FORMATS = ('png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp', 'zip')
SUPPORTED_IMAGE_VIEWS = ('grayscale','colormap','rgb')

'''List of datasources to try, in order, given a path'''
DATASOURCES = bfly_config.get(
    "datasource",
    ["hdf5", "tilespecs", "multibeam", "mojo", "regularimagestack"])

'''Paths must start with one of the following allowed paths'''
ALLOWED_PATHS = bfly_config.get("allowed-paths", [os.sep])

if bfly_config.get("suppress-tornado-logging", True):
    import logging
    logging.getLogger("tornado.access").setLevel(logging.ERROR)

all = [PORT, MAX_CACHE_SIZE, ALWAYS_SUBSAMPLE, IMAGE_RESIZE_METHOD,
       DEFAULT_OUTPUT, DATASOURCES, ALLOWED_PATHS]
