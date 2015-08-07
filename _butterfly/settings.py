import cv2

#Server settings
PORT = 2001
MAX_CACHE_SIZE = 1*1024*1024*1024 #1GB default maximum cache size
SUPPRESS_CONSOLE_OUTPUT = False

#Queries that will enable flags
ASSENT_LIST = ('yes', 'y', 'true')

#Resize settings
ALWAYS_SUBSAMPLE = True
IMAGE_RESIZE_METHOD = cv2.INTER_LINEAR

#Output settings
DEFAULT_OUTPUT = '.png'
SUPPORTED_IMAGE_FORMATS = ('png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp') #Using cv2 - please check if supported before adding!