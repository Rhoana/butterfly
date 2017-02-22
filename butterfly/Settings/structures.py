import cv2
import os

# FOR ALL NAMELESS KEYWORDS
class _nameless_struct():
    VALUE = 0
    def __init__(self,**_keywords):

        alls = []
        for key in _keywords:
            keyval = _keywords[key]
            setattr(self,key,keyval)
            # PUT ALL LISTS INTO LIST
            more = keyval if type(keyval) is list else []
            # PUT ALL TERM NAMES INTO LIST
            if hasattr(keyval, 'NAME'):
                more = [keyval.NAME]
            alls += more
        if len(alls):
            self.LIST = sorted(set(alls),key=alls.index)

    @property
    def name_value_list(self):
        get_nvl = lambda s: getattr(self, s, False)
        return map(get_nvl, ['NAME', 'VALUE', 'LIST'])

# FOR ALL KEYWORDS WITH NAMES
class _named_struct(_nameless_struct):
    def __init__(self,_name,**_keywords):
        _nameless_struct.__init__(self, **_keywords)
        self.NAME = _name

# Query params for grouping
_experiments = 'experiments'
_samples = 'samples'
_datasets = 'datasets'
_channels = 'channels'

_groupings = {
    _experiments: 'experiment',
    _samples: 'sample',
    _datasets: 'dataset',
    _channels: 'channel'
}

'''
THIS HELPS HANDLE URL REQUESTS
'''
class INPUT():
    def __init__(self):
        # ALL THE METHOD NAMES
        self.METHODS = _named_struct( 'method',
            GROUP_LIST = [
                _experiments, _samples, _datasets, _channels
            ],
            INFO_LIST = ['channel_metadata', 'entity_feature'],
            META = _named_struct('channel_metadata'),
            FEAT = _named_struct('entity_feature'),
            IMAGE_LIST = ['data', 'mask']
        )
        self.GROUP = _nameless_struct(
            LIST = map(_groupings.get, self.METHODS.GROUP_LIST)
        )
        # ALL THE FEATURE NAMES
        self.FEATURES = _named_struct( 'feature',
            POINT_LIST = ['synapse_keypoint','neuron_keypoint'],
            LINK_LIST = ['synapse_parent','neuron_children'],
            LABEL_LIST = ['synapse_ids','neuron_ids'],
            BOOL_LIST = ['is_synapse','is_neuron'],
            VOXEL_LIST = ['voxel_list']
        )
        self.POSITION = _nameless_struct(
            # ALL THE ORIGIN / SHAPE INPUTS
            X = _named_struct('x'),
            Y = _named_struct('y'),
            Z = _named_struct('z'),
            WIDTH = _named_struct('width'),
            HEIGHT = _named_struct('height'),
            DEPTH = _named_struct('depth',
                VALUE = 1
            )
        )
        # ALL THE RESOLUTION INPUTS
        self.RESOLUTION = _nameless_struct(
            XY = _named_struct('resolution'),
            X = _named_struct('x-res'),
            Y = _named_struct('y-res'),
            Z = _named_struct('z-res')
        )
        # ALL THE INFO / FEATURE INPUTS
        self.INFO = _nameless_struct(
            FORMAT = _named_struct('format',
                LIST = ['json','yaml'],
                VALUE = 'json'
            ),
            ID = _named_struct('id')
        )
        # ALL THE IMAGE INPUTS
        self.IMAGE = _nameless_struct(
            FORMAT = _named_struct('format',
                COLOR_LIST = ['png','jpg','bmp'],
                GRAY_LIST = ['tif', 'tiff'],
                ZIP_LIST = ['zip'],
                VALUE = 'png'
            ),
            VIEW = _named_struct('view',
                GRAY = _named_struct('grayscale'),
                COLOR = _named_struct('colormap'),
                RGB = _named_struct('rgb'),
                VALUE = 'grayscale'
            )
        )

'''
THIS HELPS LOAD TILES
'''
class RUNTIME():
    def __init__(self):
        # ALL THE TILE RUNTIME TERMS
        self.TILE = _nameless_struct(
            INSIDE = _nameless_struct(
                I = _named_struct('i'),
                J = _named_struct('j'),
                K = _named_struct('k'),
                SI = _named_struct('si'),
                SJ = _named_struct('sj'),
                SK = _named_struct('sk')
            ),
            OUTSIDE = _nameless_struct(
                # ALL THE ORIGIN / SHAPE INPUTS
                X = _named_struct('x'),
                Y = _named_struct('y'),
                Z = _named_struct('z')
            )
        )
        # ALL THE IMAGE RUNTIME TERMS
        self.IMAGE = _nameless_struct(
            SOURCE = _named_struct('source-type',
                LIST = [
                    'hdf5',
                    'tilespecs',
                    'mojo',
                    'regularimagestack'
                ],
                VALUE = 'hdf5'
            ),
            BLOCK = _named_struct('block-size')
        )

'''
THIS HELPS RETURN TEXT
'''
class OUTPUT():
    def __init__(self):
        # ALL THE INFO OUTPUT TERMS
        self.INFO = _nameless_struct(
            CHANNEL = _named_struct('name'),
            NAMES  = _named_struct('list'),
            PATH  = _named_struct('path'),
            TYPE = _named_struct('data-type'),
            SIZE  = _named_struct('dimensions',
                X = _named_struct('x'),
                Y = _named_struct('y'),
                Z = _named_struct('z')
            )
        )

