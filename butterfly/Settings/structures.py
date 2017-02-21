import cv2
import os

# FOR ALL NAMELESS KEYWORDS
class _nameless_struct():
    VALUE = 0
    ALL_LIST = []
    def __init__(self,**_keywords):
        for key in _keywords:
            keyval = _keywords[key]
            setattr(self,key,keyval)
            # PUT ALL LISTS INTO ALL_LIST
            more = keyval if type(keyval) is list else []
            self.ALL_LIST = self.ALL_LIST + more

# FOR ALL KEYWORDS WITH NAMES
class _named_struct(_nameless_struct):
    def __init__(self,_name,**_keywords):
        self.NAME = _name
        _nameless_struct.__init__(self, **_keywords)


# Query params for grouping
_experiments = 'experiments'
_samples = 'samples'
_datasets = 'datasets'
_channels = 'channels'

_groupings = {
    _experiments: 'experiment',
    _samples: 'sample',
    _datasets: 'dataset',
    _channels: 'channel',
}

# ALL THE METHOD NAMES
_all_methods = _named_struct( 'method',
    GROUP_LIST = [_experiments, _samples, _datasets, _channels],
    INFO_LIST = ['channel_metadata', 'entity_feature'],
    IMAGE_LIST = ['data', 'mask']
)

# AL FEATURES FOR ENTITY METHOD
_all_features = _named_struct( 'feature',
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
_group_input = map(_groupings.get, _all_methods.GROUP_LIST)
_scale_input = ['resolution','x-res','y-res','z-res']
_info_input = ['format','id']
_image_input = ['format','view']

# INPUT WHITELISTS AND VALUES
_info_formats = ['json','yaml']
_image_views = ['grayscale','colormap','rgb']
_image_formats = ['png', 'jpg', 'tif', 'bmp', 'zip']
_source_formats = ['hdf5', 'tilespecs', 'mojo']
_source_formats.append('regularimagestack')
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


'''
THIS HELPS HANDLE URL REQUESTS
'''
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
        self.X = _named_struct(_image_origin[0])
        self.Y = _named_struct(_image_origin[1])
        self.Z = _named_struct(_image_origin[2])
        self.WIDTH = _named_struct(_image_shape[0])
        self.HEIGHT = _named_struct(_image_shape[1])
        self.DEPTH = _named_struct(_image_shape[2])
        # ALL THE RESOLUTION INPUTS
        self.RESOLUTION = _nameless_struct(
            XY = _named_struct(_scale_input[0]),
            X = _named_struct(_scale_input[1]),
            Y = _named_struct(_scale_input[2]),
            Z = _named_struct(_scale_input[3])
        )
        # ALL THE INFO / FEATURE INPUTS
        self.INFO = _nameless_struct(
            FORMAT = _named_struct(_info_input[0],
                LIST = _info_formats,
                VALUE = _info_default
            ),
            ID = _named_struct(_info_input[1])
        )
        # ALL THE IMAGE INPUTS
        self.IMAGE = _nameless_struct(
            FORMAT = _named_struct(_image_input[0],
                LIST = _image_formats,
                VALUE = _image_default
            ),
            VIEW = _named_struct(_image_input[1],
                LIST = _image_views,
                VALUE = _view_default
            )
        )

'''
THIS HELPS LOAD TILES
'''
class RUNTIME():
    #ALL THE LISTS OF RUNTIME NAMES
    ORIGIN_LIST = _image_origin
    SHAPE_LIST = _image_shape
    PIXEL_LIST = _pixels_runtime
    SCALE_LIST = _scale_runtime
    IMAGE_LIST = _image_runtime
    def __init__(self):
        # ALL THE ORIGIN / SHAPE INPUTS
        self.X = _named_struct(_image_origin[0])
        self.Y = _named_struct(_image_origin[1])
        self.Z = _named_struct(_image_origin[2])
        self.WIDTH = _named_struct(_image_shape[0])
        self.HEIGHT = _named_struct(_image_shape[1])
        self.DEPTH = _named_struct(_image_shape[2])
        # ALL THE TILE RUNTIME TERMS
        self.TILE = _nameless_struct(
            I = _named_struct(_pixels_runtime[0]),
            J = _named_struct(_pixels_runtime[1]),
            K = _named_struct(_pixels_runtime[2]),
            SI = _named_struct(_scale_runtime[0]),
            SJ = _named_struct(_scale_runtime[1]),
            SK = _named_struct(_scale_runtime[2])
        )
        # ALL THE IMAGE RUNTIME TERMS
        self.IMAGE = _nameless_struct(
            SOURCE = _named_struct(_image_runtime[0],
                LIST = _source_formats,
                VALUE = _source_default
            ),
            BLOCK = _named_struct(_image_runtime[1]),
            PATH = _named_struct(_image_runtime[2])
        )

'''
THIS HELPS RETURN TEXT
'''
class OUTPUT():
    #ALL THE LISTS OF VALUE NAMES
    INFO_LIST = _info_output
    IMAGE_LIST = _image_output
    def __init__(self):
        # ALL THE INFO OUTPUT TERMS
        self.INFO = _nameless_struct(
            NAME = _named_struct(_info_output[0]),
            LIST  = _named_struct(_info_output[1]),
            PATH  = _named_struct(_info_output[2]),
            TYPE = _named_struct(_image_output[0]),
            SIZE  = _named_struct(_image_output[1],
                X = _named_struct(_image_origin[0]),
                Y = _named_struct(_image_origin[1]),
                Z = _named_struct(_image_origin[2])
            )
        )

