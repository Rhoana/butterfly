from rh_config import config
import cv2
import os

bfly_config = config.get("bfly", {})
# Server settings

#HTTP port for server
PORT = int(bfly_config.get("port", 2001))

#Maximum size of the cache in MiB: 1 GiB by default
_max_cache = bfly_config.get("max-cache-size", 1024)
MAX_CACHE_SIZE = int(_max_cache) * (1024**2)

#Queries that will enable flags
ASSENT_LIST = bfly_config.get("assent-list", ('yes', 'y', 'true'))

# Output settings
_default_format = 'png'
_default_view = 'grayscale'
# Using cv2 - please check if supported before adding!
_supported_formats = ('png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp', 'zip')
_supported_views = ('grayscale','colormap','rgb')

#List of datasources to try, in order, given a path
_datasources = ["hdf5", "tilespecs", "mojo", "regularimagestack"]
DATASOURCES = bfly_config.get("datasource", _datasources)

#Paths must start with one of the following allowed paths
ALLOWED_PATHS = bfly_config.get("allowed-paths", [os.sep])

# Combined output settings
FORMAT_LIST = ['format', _supported_formats, _default_format]
VIEW_LIST = ['view', _supported_views, _default_view]

# Query params for grouping
_experiments = "experiments"
_samples = "samples"
_datasets = "datasets"
_channels = "channels"
_metadata = 'channel_metadata'

GROUPINGS = {
    _experiments: 'experiment',
    _samples: 'sample',
    _datasets: 'dataset',
    _channels: 'channel',
    _metadata: ''
}

RANKINGS = [_experiments, _samples, _datasets]
RANKINGS = RANKINGS + [_channels, _metadata]

TILETERMS = ['format','view','path','disk-format']
DATATERMS = ['data-type','block-size','dimensions']
POSITION = ['x','y','z','width','height','resolution']
INFOTERMS = ['name','method','list','short-description','id']

METHODS = ['synapse_ids','neuron_ids','is_synapse','is_neuron']
METHODS = METHODS + ['synapse_keypoint','neuron_keypoint']
METHODS = METHODS + ['synapse_parent','neuron_children']
METHODS = METHODS + ['entity_feature','voxel_list']
DATAMETHODS = ['data','mask']

all = [INFOTERMS, TILETERMS, DATATERMS, DATAMETHODS]
all = all + [ALLOWED_PATHS, DATASOURCES, ASSENT_LIST]
all = all + [MAX_CACHE_SIZE, PORT, POSITION, METHODS]
all = all + [FORMAT_LIST, VIEW_LIST]
all = all + [GROUPINGS, RANKINGS]
