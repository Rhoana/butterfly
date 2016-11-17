import logging
import numpy as np
import urllib2

import settings
from collections import OrderedDict
import rh_logger


class Core(object):

    def __init__(self):
        '''
        '''
        self._datasources = {}
        self.vol_xy_start = [0, 0]
        self.tile_xy_start = [0, 0]
        self._cache = OrderedDict()
        self._max_cache_size = settings.MAX_CACHE_SIZE
        self._current_cache_size = 0

    def get(self,datapath, start_coord, vol_size, **kwargs):
        '''
        Request a subvolume of the datapath at a given zoomlevel.
        '''
        presets = {
            'segmentation': False,
            'segcolor': False,
            'fit': False,
            'w': 0,
            'dtype': np.uint8,
            'synapse': False
        }
        for k,v in presets.iteritems():
            kwargs.setdefault(k,v)

        segmentation= kwargs['segmentation']
        segcolor= kwargs['segcolor']
        synapse=kwargs['synapse']
        dtype= kwargs['dtype']
        fit= kwargs['fit']
        w= kwargs['w']


        # if datapath is not indexed (knowing the meta information),
        # do it now
        if datapath not in self._datasources:
            self.create_datasource(datapath, dtype=dtype)

        datasource = self._datasources[datapath]

        planes = []
        scale = 2 ** w
        [x0,y0] = np.array(start_coord) * scale
        [x1,y1] = np.array(vol_size) + [x0,y0]
        try:
            rh_logger.logger.report_event('Loading tiles:')
            for z in range(start_coord[2], start_coord[2] + vol_size[2]):
                plane = datasource.load_cutout(x0, x1, y0, y1, z, w)
                planes.append(plane)
            return np.dstack(planes)
        except:
            rh_logger.logger.report_exception()

        # If we need to fit the volume to existing data, calculate volume size
        # now
        if fit:
            boundaries = datasource.get_boundaries()
            # No mip zoom for slices right now
            boundaries = [boundaries[0] //
                          (2**w), boundaries[1] //
                          (2**w), boundaries[2]]
            for i in range(3):
                if start_coord[i] + vol_size[i] > boundaries[i]:
                    vol_size[i] = boundaries[i] - start_coord[i]

        # Use modified segmentation flag to support synapses
        segmentation = 2 if synapse else segmentation

        # Use 4D volume for rgb data
        color = segcolor
        if color:
            vol = np.zeros(
                (vol_size[1],
                 vol_size[0],
                    vol_size[2],
                    3),
                dtype=np.uint16)
        else:
            vol = np.zeros(
                (vol_size[1],
                 vol_size[0],
                    vol_size[2]),
                dtype=np.uint32)

    def create_datasource(self, datapath, dtype=np.uint8):
        '''
        '''

        for allowed_path in settings.ALLOWED_PATHS:
            if datapath.startswith(allowed_path):
                break
        else:
            raise urllib2.HTTPError(
                None, 403, datapath + " is not an allowed datapath. " +
                "Contact the butterfly admin to configure a new datapath",
                [], None)
        for datasource in settings.DATASOURCES:
            try:
                if datasource == 'mojo':
                    from mojo import Mojo
                    ds = Mojo(self, datapath)
                    break
                elif datasource == 'regularimagestack':
                    from regularimagestack import RegularImageStack
                    ds = RegularImageStack(self, datapath)
                    break
                elif datasource in ("tilespecs"):
                    from tilespecs import Tilespecs
                    ds = Tilespecs(self, datapath, dtype=dtype)
                    break
                elif datasource in ("comprimato", "multibeam"):
                    from multibeam import MultiBeam
                    ds = MultiBeam(self, datapath, dtype=dtype)
                    break
                elif datasource == 'hdf5':
                    from hdf5 import HDF5DataSource
                    ds = HDF5DataSource(self, datapath, dtype=dtype)
                    break
            except:
                rh_logger.logger.report_event(
                    "Can't load %s with %s" % (datapath, datasource),
                    log_level=logging.DEBUG)
                continue
        else:
            rh_logger.logger.report_event(
                "Failed to find datasource for %s" % datapath,
                log_level=logging.WARNING)
            raise urllib2.HTTPError(
                None, 404, "Can't find a loader for datapath=%s" % datapath,
                [], None)
        # call index
        ds.index()

        self._datasources[datapath] = ds

    def get_datasource(self,datapath):
        return self._datasources[datapath]
