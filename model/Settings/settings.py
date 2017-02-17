from rh_config import config
import cv2
import os

BFLY_CONFIG = config.get("bfly", {})
# Server settings

#HTTP port for server
PORT = int(BFLY_CONFIG.get("port", 2001))

#Maximum size of the cache in MiB: 1 GiB by default
_max_cache = BFLY_CONFIG.get("max-cache-size", 1024)
MAX_CACHE_SIZE = int(_max_cache) * (1024**2)

#Queries that will enable flags
ASSENT_LIST = BFLY_CONFIG.get("assent-list", ('yes', 'y', 'true'))

# Output settings
_default_format = 'png'
_default_view = 'grayscale'
# Using cv2 - please check if supported before adding!
_supported_formats = ('png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp', 'zip')
_supported_views = ('grayscale','colormap','rgb')

#List of datasources to try, in order, given a path
DATASOURCES = ["hdf5", "tilespecs", "mojo", "regularimagestack"]

#Paths must start with one of the following allowed paths
ALLOWED_PATHS = BFLY_CONFIG.get("allowed-paths", [os.sep])

# Combined output settings
TEXT_FORMAT_LIST = ['format', ('json','yaml'), 'json']
FORMAT_LIST = ['format', _supported_formats, _default_format]
VIEW_LIST = ['view', _supported_views, _default_view]

# Query params for grouping
_experiments = "experiments"
_samples = "samples"
_datasets = "datasets"
_channels = "channels"
_metadata = 'channel_metadata'
_entity = 'entity_feature'

_groupings = {
    _experiments: 'experiment',
    _samples: 'sample',
    _datasets: 'dataset',
    _channels: 'channel',
}

GROUPMETHODS = [_experiments, _samples, _datasets, _channels]
INFOMETHODS = [_metadata, _entity]
DATAMETHODS = ['data','mask']

GROUPTERMS = map(_groupings.get, GROUPMETHODS)
TILETERMS = ['s','i','j','k']
INFOTERMS = ['name','method','list','feature']
INFOTERMS = INFOTERMS + ['short-description','id']
DATATERMS = ['data-type','block-size','dimensions']
SOURCETERMS = ['format','view','path','disk-format']
POSITION = ['x','y','z','width','height','depth','resolution']

FEATURES = ['synapse_ids','neuron_ids','is_synapse','is_neuron']
FEATURES = FEATURES + ['synapse_keypoint','neuron_keypoint']
FEATURES = FEATURES + ['synapse_parent','neuron_children']
FEATURES = FEATURES + ['voxel_list']

