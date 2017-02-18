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

# FOR ALL NAMELESS KEYWORDS
class _nameless():
    def __init__(self,**_keywords):
        for key in _keywords:
            setattr(self,key,_keywords[key])

# FOR ALL KEYWORDS WITH NAMES AND VALUES
class _name_value(_nameless):
    def __init__(self,_name,**_keywords):
        _nameless.__init__(self, **_keywords)
        self.NAME = _name
        self.VALUE = 0

# Query params for grouping
_experiments = "experiments"
_samples = "samples"
_datasets = "datasets"
_channels = "channels"

_groupings = {
    _experiments: 'experiment',
    _samples: 'sample',
    _datasets: 'dataset',
    _channels: 'channel',
}

# ALL THE METHOD NAMES
_group_list = [_experiments, _samples, _datasets, _channels]
_basic_input = ['method','feature']
_metadata = 'channel_metadata'
_entity = 'entity_feature'
_image = 'data'
_mask = 'mask'

_all_methods = _name_value( _basic_input[0],
    INFO_LIST = [_metadata, _entity],
    IMAGE_LIST = [_image, _mask],
    GROUP_LIST = _group_list
)

# AL FEATURES FOR ENTITY METHOD
_all_features = _name_value( _basic_input[1],
    POINT_LIST = ['synapse_keypoint','neuron_keypoint'],
    LINK_LIST = ['synapse_parent','neuron_children'],
    LABEL_LIST = ['synapse_ids','neuron_ids'],
    BOOL_LIST = ['is_synapse','is_neuron'],
    VOXEL_LIST = ['voxel_list']
)

# TERMS USED FOR POSITION
_image_origin = ['x','y','z']
_image_shape = ['width','height','depth']

# DATA SENT IN INPUT
_group_input = map(_groupings.get, _group_list)
_scale_input = ['resolution','x-res','y-res','z-res']
_info_input = ['format','id']
_image_input = ['format','view']

# INPUT WHITELISTS AND DEFAULTS
_info_formats = ['json','yaml']
_image_views = ['grayscale','colormap','rgb']
_image_formats = ['png', 'jpg', 'tif', 'bmp', 'zip']
_source_formats = ["hdf5", "tilespecs", "mojo"]
_source_formats.append("regularimagestack")
_info_default = 'json'
_view_default = 'grayscale'
_source_default = 'hdf5'
_image_default = 'png'

# DATA USED DURING RUNTIME
_pixels_runtime = ['i','j','k']
_scale_runtime = ['si','sj','sk']
_image_runtime = ['source-type','block-size','path']

# DATA OUTPUT IN REQUESTS
_image_output = ['data-type','dimensions','path']
_info_output = ['name','list','path']


"""
THIS HELPS HANDLE URL REQUESTS
"""
class INPUT():
    # ALL THE BASIC INPUT LISTS
    METHODS = _all_methods
    FEATURES = _all_features
    # ALL THE LISTS OF INPUT NAMES
    ORIGIN_LIST = _image_origin
    SHAPE_LIST = _image_shape
    SCALE_LIST = _scale_input
    INFO_LIST = _info_input
    IMAGE_LIST = _image_input
    GROUP_LIST = _group_input
    def __init__(self):
        # ALL THE ORIGIN / SHAPE INPUTS
        self.X = _name_value(_image_origin[0])
        self.Y = _name_value(_image_origin[1])
        self.Z = _name_value(_image_origin[2])
        self.WIDTH = _name_value(_image_shape[0])
        self.HEIGHT = _name_value(_image_shape[1])
        self.DEPTH = _name_value(_image_shape[2])
        # ALL THE RESOLUTION INPUTS
        self.RESOLUTION = _nameless(
            XY = _name_value(_scale_input[0]),
            X = _name_value(_scale_input[1]),
            Y = _name_value(_scale_input[2]),
            Z = _name_value(_scale_input[3])
        )
        # ALL THE INFO / FEATURE INPUTS
        self.INFO = _nameless(
            FORMAT = _name_value(_info_input[0],
                LIST = _info_formats,
                DEFAULT = _info_default
            ),
            ID = _name_value(_info_input[1])
        )
        # ALL THE IMAGE INPUTS
        self.IMAGE = _nameless(
            FORMAT = _name_value(_image_input[0],
                LIST = _image_formats,
                DEFAULT = _image_default
            ),
            VIEW = _name_value(_image_input[1],
                LIST = _image_views,
                DEFAULT = _view_default
            )
        )

"""
THIS HELPS LOAD TILES
"""
class RUNTIME():
    #ALL THE LISTS OF RUNTIME NAMES
    ORIGIN_LIST = _image_origin
    SHAPE_LIST = _image_shape
    PIXEL_LIST = _pixels_runtime
    SCALE_LIST = _scale_runtime
    IMAGE_LIST = _image_runtime
    def __init__(self):
        # ALL THE ORIGIN / SHAPE INPUTS
        self.X = _name_value(_image_origin[0])
        self.Y = _name_value(_image_origin[1])
        self.Z = _name_value(_image_origin[2])
        self.WIDTH = _name_value(_image_shape[0])
        self.HEIGHT = _name_value(_image_shape[1])
        self.DEPTH = _name_value(_image_shape[2])
        # ALL THE TILE RUNTIME TERMS
        self.TILE = _nameless(
            I = _name_value(_pixels_runtime[0]),
            J = _name_value(_pixels_runtime[1]),
            K = _name_value(_pixels_runtime[2]),
            SI = _name_value(_scale_runtime[0]),
            SJ = _name_value(_scale_runtime[1]),
            SK = _name_value(_scale_runtime[2])
        )
        # ALL THE IMAGE RUNTIME TERMS
        self.IMAGE = _nameless(
            SOURCE = _name_value(_image_runtime[0],
                LIST = _source_formats,
                DEFAULT = _source_default
            ),
            BLOCK = _name_value(_image_runtime[1]),
            PATH = _name_value(_image_runtime[2])
        )

"""
THIS HELPS RETURN TEXT
"""
class OUTPUT():
    #ALL THE LISTS OF VALUE NAMES
    INFO_LIST = _info_output
    IMAGE_LIST = _image_output
    def __init__(self):
        # ALL THE INFO OUTPUT TERMS
        self.INFO = _nameless(
            NAME = _name_value(_info_output[0]),
            LIST  = _name_value(_info_output[1]),
            PATH  = _name_value(_info_output[2]),
            TYPE = _name_value(_image_output[0]),
            SIZE  = _name_value(_image_output[1],
                X = _name_value(_image_origin[0]),
                Y = _name_value(_image_origin[1]),
                Z = _name_value(_image_origin[2])
            )
        )

