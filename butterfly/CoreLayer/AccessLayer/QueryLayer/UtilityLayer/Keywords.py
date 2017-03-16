from Settings import MAX_CACHE_SIZE
from Settings import CONFIG_FILENAME
from Structures import NamelessStruct
from Structures import NamedStruct

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

_group_list = [_experiments, _samples, _datasets, _channels]

'''
THIS HELPS HANDLE URL REQUESTS
'''
class INPUT():
    def __init__(self):
        # ALL THE METHOD NAMES
        self.METHODS = NamedStruct( 'method',
            INFO_LIST = ['channel_metadata', 'entity_feature'],
            META = NamedStruct('channel_metadata'),
            FEAT = NamedStruct('entity_feature'),
            IMAGE_LIST = ['data', 'mask'],
            GROUP_LIST = _group_list
        )
        self.GROUP = NamedStruct( 'name',
            LIST = map(_groupings.get, self.METHODS.GROUP_LIST)
        )
        # ALL THE FEATURE NAMES
        self.FEATURES = NamedStruct( 'feature',
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
            SYNAPSE_LINKS = NamedStruct('synapse_parent'),
            NEURON_CHILDREN = NamedStruct('neuron_children'),
            POINT_LIST = ['synapse_keypoint','neuron_keypoint'],
            LINK_LIST = ['synapse_parent','neuron_children'],
            LABEL_LIST = ['synapse_ids','neuron_ids'],
            BOOL_LIST = ['is_synapse','is_neuron'],
            VOXEL_LIST = ['voxel_list']
        )
        self.POSITION = NamelessStruct(
            # ALL THE ORIGIN / SHAPE INPUTS
            X = NamedStruct('x'),
            Y = NamedStruct('y'),
            Z = NamedStruct('z'),
            WIDTH = NamedStruct('width'),
            HEIGHT = NamedStruct('height'),
            DEPTH = NamedStruct('depth',
                VALUE = 1
            )
        )
        # ALL THE RESOLUTION INPUTS
        self.RESOLUTION = NamelessStruct(
            XY = NamedStruct('resolution',
                VALUE = 0
            ),
            X = NamedStruct('x-res'),
            Y = NamedStruct('y-res'),
            Z = NamedStruct('z-res')
        )
        # ALL THE INFO / FEATURE INPUTS
        self.INFO = NamelessStruct(
            FORMAT = NamedStruct('format',
                LIST = ['json','yaml'],
                VALUE = 'json'
            ),
            ID = NamedStruct('id')
        )
        # ALL THE IMAGE INPUTS
        self.IMAGE = NamelessStruct(
            FORMAT = NamedStruct('format',
                COLOR_LIST = ['png','jpg','bmp'],
                TIF_LIST = ['tif', 'tiff'],
                ZIP_LIST = ['zip'],
                VALUE = 'png'
            ),
            VIEW = NamedStruct('view',
                GRAY = NamedStruct('grayscale'),
                COLOR = NamedStruct('colormap'),
                RGB = NamedStruct('rgb'),
                VALUE = 'grayscale'
            )
        )

'''
THIS HELPS LOAD TILES
'''
class RUNTIME():
    def __init__(self):
        # ALL THE TILE RUNTIME TERMS
        self.TILE = NamelessStruct(
            KJI = NamedStruct('kji'),
            SCALES = NamedStruct('scales'),
            ZYX = NamedStruct('zyx')
        )
        # ALL THE IMAGE RUNTIME TERMS
        self.IMAGE = NamelessStruct(
            SOURCE = NamedStruct('source-type',
                LIST = [
                    'hdf5',
                    'tilespecs',
                    'mojo',
                    'regularimagestack'
                ],
                HDF5 = NamedStruct('hdf5',
                    OUTER = NamedStruct('filename'),
                    INNER = NamedStruct('dataset-path',
                        VALUE = 'main'
                    )
                ),
                VALUE = 'regularimagestack'
            ),
            BLOCK = NamedStruct('block-size',
                VALUE = [1, 512, 512]
            )
        )
        # ALL THE CACHE RUNTIME TERMS
        self.CACHE = NamelessStruct(
            META = NamedStruct('meta-size',
                VALUE = 567
            ),
            MAX = NamedStruct('max-cache-size',
                VALUE = MAX_CACHE_SIZE
            )
        )
        # ALL THE DATABASE RUNTIME TERMS
        self.DB = NamelessStruct(
            TABLE = NamelessStruct(
                LIST = ['neuron', 'synapse'],
                NEURON = NamedStruct('neuron',
                    KEY = NamedStruct('neuron'),
                    KEY_LIST = ['neuron']
                ),
                SYNAPSE = NamedStruct('synapse',
                    KEY = NamedStruct('__id'),
                    NEURON_LIST = ['n1','n2'],
                    KEY_LIST = ['n1','n2']
                ),
                ALL = NamelessStruct(
                    POINT_LIST = ['z','y','x']
                )
            ),
            FILE = NamelessStruct(
                SYNAPSE = NamedStruct('synapse-connections.json',
                    NEURON_LIST = ['neuron_1','neuron_2'],
                    POINT  = NamedStruct('synapse_center',
                        LIST = ['z','y','x']
                    )
                ),
                CONFIG = NamedStruct(CONFIG_FILENAME,
                    GROUP_LIST = _group_list,
                    PATH = NamedStruct('path')
                )
            ),
            JOIN = NamedStruct('{}://{}')
        )
        # ALL THE ERROR RUNTIME TERMS
        self.ERROR = NamelessStruct(
            TERM = NamedStruct('term'),
            OUT = NamedStruct('value'),
            SIZE = NamedStruct('size'),
            CHECK = NamedStruct('check'),
            REQUEST = NamelessStruct(
                CHECK = NamedStruct('bad_check',
                    LOG = 'info',
                    ACT = '''
The {term} {value} is not {check}.
                    '''.replace('\n','')
                )
            ),
            SERVER = NamelessStruct(
                START = NamedStruct('start',
                    LOG = 'info',
                    ACT = '''
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
    Running server on port {value}.
_______________________________________
                    '''
                ),
                STOP = NamedStruct('stop',
                    LOG = 'info',
                    ACT = '''
|||||||||||||||||||||||||||||||||||||||
    Closed server on port {value}.
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
                    '''
                )
            ),
            CACHE = NamelessStruct(
                ADD = NamedStruct('add_query',
                    LOG = 'info',
                    ACT = '''
Add {value} to cache. Cache now {size} bytes.
                    '''.replace('\n','')
                ),
                MAX = NamedStruct('over_max',
                    LOG = 'warning',
                    ACT = '''
Cannot cache {value}. {size} bytes is over max.
                    '''.replace('\n','')
                )
            ),
        )

'''
THIS HELPS RETURN TEXT
'''
class OUTPUT():
    def __init__(self):
        # ALL THE INFO OUTPUT TERMS
        self.INFO = NamelessStruct(
            CHANNEL = NamedStruct('name'),
            NAMES  = NamedStruct('list'),
            PATH  = NamedStruct('path'),
            TYPE = NamedStruct('data-type',
                VALUE = 'uint8',
                RAW_LIST = ['uint8','float32'],
                ID_LIST = ['uint16','uint32']
            ),
            SIZE  = NamedStruct('dimensions',
                X = NamedStruct('x'),
                Y = NamedStruct('y'),
                Z = NamedStruct('z')
            )
        )

