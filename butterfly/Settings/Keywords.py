from Settings import MAX_CACHE_SIZE
from Structures import _nameless_struct
from Structures import _named_struct

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
        self.GROUP = _named_struct( 'name',
            LIST = map(_groupings.get, self.METHODS.GROUP_LIST)
        )
        # ALL THE FEATURE NAMES
        self.FEATURES = _named_struct( 'feature',
            NEURON_LIST = [
                'neuron_keypoint',
                'neuron_ids',
                'is_neuron'
            ],
            SYNAPSE_LIST = [
                'synapse_keypoint',
                'neuron_children',
                'synapse_parent',
                'synapse_ids',
                'is_synapse'
            ],
            SYNAPSE_LINKS = _named_struct('synapse_parent'),
            NEURON_CHILDREN = _named_struct('neuron_children'),
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
            XY = _named_struct('resolution',
                VALUE = 0
            ),
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
                TIF_LIST = ['tif', 'tiff'],
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
            KJI = _named_struct('kji'),
            SCALES = _named_struct('scales'),
            ZYX = _named_struct('zyx')
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
                HDF5 = _named_struct('hdf5',
                    OUTER = _named_struct('filename'),
                    INNER = _named_struct('dataset-path',
                        VALUE = 'main'
                    )
                ),
                VALUE = 'regularimagestack'
            ),
            BLOCK = _named_struct('block-size',
                VALUE = [1, 512, 512]
            )
        )
        # ALL THE CACHE RUNTIME TERMS
        self.CACHE = _nameless_struct(
            META = _named_struct('meta-size',
                VALUE = 567
            ),
            MAX = _named_struct('max-cache-size',
                VALUE = MAX_CACHE_SIZE
            )
        )
        # ALL THE DATABASE RUNTIME TERMS
        self.DB = _nameless_struct(
            TABLE = _nameless_struct(
                LIST = ['neuron', 'synapse'],
                NEURON = _named_struct('neuron',
                    KEY = _named_struct('neuron'),
                    KEY_LIST = ['neuron']
                ),
                SYNAPSE = _named_struct('synapse',
                    KEY = _named_struct('__id'),
                    NEURON_LIST = ['n1','n2'],
                    KEY_LIST = ['n1','n2']
                ),
                ALL = _nameless_struct(
                    POINT_LIST = ['z','y','x']
                )
            ),
            FILE = _nameless_struct(
                SYNAPSE = _named_struct('synapse-connections.json',
                    NEURON_LIST = ['neuron_1','neuron_2'],
                    POINT  = _named_struct('synapse_center',
                        LIST = ['z','y','x']
                    )
                )
            ),
            JOIN = _named_struct('{}://{}')
        )
        # ALL THE ERROR RUNTIME TERMS
        self.ERROR = _nameless_struct(
            TERM = _named_struct('term'),
            OUT = _named_struct('value'),
            CHECK = _named_struct('check')
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
            TYPE = _named_struct('data-type',
                VALUE = 'uint8',
                RAW_LIST = ['uint8','float32'],
                ID_LIST = ['uint16','uint32']
            ),
            SIZE  = _named_struct('dimensions',
                X = _named_struct('x'),
                Y = _named_struct('y'),
                Z = _named_struct('z')
            )
        )

