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

# List all groups for the API and the rh-config
_group_list = [_experiments, _samples, _datasets, _channels]
# List all tables for the API and the database
_table_list = ['neuron', 'synapse']

class INPUT():
    """ Keywords to read input files and requests

    All the attributes and their attributes store \ 
    a mutable VALUE of and type, and some store a \ 
    static NAME that should always be used externally.

    Attributes
    ------------
    METHODS : :class:`NamedStruct`
        All methods for :class:`RequestHandler` requests
    GROUP : :class:`NamedStruct`
        All groups from the :data:`UtilityLayer.BFLY_CONFIG`
    FEATURES : :class:`NamedStruct`
        All features for /api/entity_feature requests
    POSITION : :class:`NamelessStruct`
        Center coordintates for :meth:`Database.load_config`
        All coordinates for :class:`RequestHandler` requests
    RESOLUTION : :class:`NamelessStruct`
        All resolutions for :class:`RequestHandler` requests
    INFO : :class:`NamelessStruct`
        Formats for /api/channel_metadata requests \ 
        and id for /api/entity_feature requests
    IMAGE : :class:`NamelessStruct`
        Formats and views for :class:`RequestHandler`\ 
        data or mask requests.
    """

    def __init__(self):
        # ALL THE METHOD NAMES
        self.METHODS = NamedStruct('method',
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
        self.FEATURES = NamedStruct('feature',
            TABLES = NamelessStruct(
                NEURON = NamedStruct(_table_list[0],
                    LIST = [
                        'neuron_keypoint',
                        'neuron_ids',
                        'is_neuron'
                    ]
                ),
                SYNAPSE = NamedStruct(_table_list[1],
                    LIST = [
                        'synapse_keypoint',
                        'neuron_children',
                        'synapse_parent',
                        'synapse_ids',
                        'is_synapse'
                    ]
                )
            ),
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
    """ Keywords passed between classes and layers.
    All the attributes and their attributes store \ 
    a mutable VALUE of and type, and some store a \ 
    static NAME that should always be used externally.

    Attributes
    ------------
    TILE : :class:`NamelessStruct`
        For :class:`QueryLayer.TileQuery`
    IMAGE : :class:`NamelessStruct`
        For :class:`QueryLayer.DataQuery`
    CACHE : :class:`NamelessStruct`
        For :class:`CoreLayer.Cache`
    DB : :class:`NamelessStruct`
        For :mod:`DatabaseLayer`
    ERROR : :class:`NamelessStruct`
        For :class:`MakeLog`
    """

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
                LIST = _table_list,
                NEURON = NamedStruct(_table_list[0],
                    KEY = NamedStruct('neuron'),
                    KEY_LIST = ['neuron']
                ),
                SYNAPSE = NamedStruct(_table_list[1],
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
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
 Start server on port {value}.
_______________________________
                    '''
                ),
                STOP = NamedStruct('stop',
                    LOG = 'info',
                    ACT = '''
|||||||||||||||||||||||||||||||
 Stop server on port {value}.
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
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

class OUTPUT():
    """ Keywords used for writing out from server.
    All the attributes and their attributes store \ 
    a mutable VALUE of and type, and some store a \ 
    static NAME that should always be used externally.

    Attributes
    ------------
    INFO : :class:`NamelessStruct`
        Outputs for /api/channel_metadata requests
    FEATURES : :class:`NamelessStruct`
        Outputs for /api/entity_feature requests
    """
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
        # ALL THE FEATURE OUTPUT TERMS
        self.FEATURES = NamelessStruct(
            LINKS = NamelessStruct(
                ID = NamedStruct('synapse_id'),
                PRE = NamedStruct('synapse_parent_pre'),
                POST = NamedStruct('synapse_parent_post')
            )
        )

