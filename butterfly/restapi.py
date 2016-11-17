from tornado.web import RequestHandler
import json
from urllib2 import HTTPError
import cv2
import numpy as np

import rh_logger
import settings


class RestAPIHandler(RequestHandler):
    '''Request handler for the documented public Butterfly REST API'''
    #
    # Query params
    #
    Q_EXPERIMENT = "experiment"
    Q_SAMPLE = "sample"
    Q_DATASET = "dataset"
    Q_CHANNEL = "channel"
    '''Encode image/mask in this image format (e.g. "tif")'''
    Q_FORMAT = "format"
    Q_X = "x"
    Q_Y = "y"
    Q_Z = "z"
    Q_WIDTH = "width"
    Q_HEIGHT = "height"
    Q_RESOLUTION = "resolution"
    #
    # Hierarchy of data organization in config file
    #
    EXPERIMENTS = "experiments"
    SAMPLES = "samples"
    DATASETS = "datasets"
    CHANNELS = "channels"

    NAME = "name"
    PATH = "path"
    SHORT_DESCRIPTION = "short-description"
    DATA_TYPE = "data-type"
    DIMENSIONS = "dimensions"
    X = "x"
    Y = "y"
    Z = "z"

    def initialize(self, core):
        '''Override of RequestHandler.initialize

        Initializes the RestAPI request handler

        :param core: the butterfly.core instance used to fetch images
        '''
        self.core = core

    def get(self, command):
        '''Handle an HTTP GET request'''

        rh_logger.logger.report_event("GET " + self.request.uri)
        try:
            if command == "experiments":
                result = self.get_experiments()
            elif command == "samples":
                result = self.get_samples()
            elif command == "datasets":
                result = self.get_datasets()
            elif command == "channels":
                result = self.get_channels()
            elif command == "channel_metadata":
                result = self.get_channel_metadata()
            elif command == "data":
                self.get_data()
                return
            elif command == "mask":
                self.get_mask()
                return
            else:
                raise HTTPError(self.request.uri, 400,
                                "Unsupported command: " + command,
                                [], None)
            data = json.dumps(result)
            self.set_header("Content-Type", "application/json")
            self.write(data)
        except HTTPError, http_error:
            self.set_status(http_error.code)
            self.set_header('Content-Type', "text/plain")
            self.write(http_error.msg)

    def _get_config(self,kind):
        '''Get the config dictionary for a named kind'''
        target = self._get_query_param(kind['param'])
        for d in kind['parent'].get(kind['plural'],[]):
            if d[self.NAME] == target:
                return d
        else:
            msg = 'Unknown '+kind['name']+': '+ target
            rh_logger.logger.report_event(msg)
            raise HTTPError(self.request.uri, 400, msg, [], None)

    def get_experiments(self):
        '''Handle the /api/experiments GET request'''
        experiments = settings.bfly_config.get(self.EXPERIMENTS, [])
        return [_[self.NAME] for _ in experiments]

    def _get_experiment_config(self):
        return self._get_config({
            'parent': settings.bfly_config,
            'plural': self.EXPERIMENTS,
            'param': self.Q_EXPERIMENT,
            'name': 'experiment name'
        })

    def get_samples(self):
        '''Handle the /api/samples GET request'''
        experiment = self._get_experiment_config()
        return [_[self.NAME] for _ in experiment.get(self.SAMPLES, [])]

    def _get_sample_config(self):
        return self._get_config({
            'parent': self._get_experiment_config(),
            'plural': self.SAMPLES,
            'param': self.Q_SAMPLE,
            'name': 'sample name'
        })

    def get_datasets(self):
        '''Handle the /api/datasets GET request'''
        sample = self._get_sample_config()
        return [_[self.NAME] for _ in sample.get(self.DATASETS, [])]

    def _get_dataset_config(self):
        return self._get_config({
            'parent': self._get_sample_config(),
            'plural': self.DATASETS,
            'param': self.Q_DATASET,
            'name': 'dataset name'
        })

    def get_channels(self):
        '''Handle the /api/channels GET request'''
        dataset = self._get_dataset_config()
        return [_[self.NAME] for _ in dataset.get(self.CHANNELS, [])]

    def _get_channel_config(self):
        return self._get_config({
            'parent': self._get_dataset_config(),
            'plural': self.CHANNELS,
            'param': self.Q_CHANNEL,
            'name': 'channel'
        })

    def get_channel_metadata(self):
        '''Handle the /api/channel_metadata GET request'''
        channel = self._get_channel_config().copy()
        # if self.PATH in channel:
        #     del channel[self.PATH]
        return channel

    def _get_query_param(self, qparam):
        result = self.get_query_argument(qparam, default=None)
        if result is None:
            rh_logger.logger.report_event(
                "Received REST API call without %s query param" % qparam)
            raise HTTPError(
                self.request.uri, 400, "Missing %s parameter" % qparam,
                [], None)
        return result

    def _get_int_query_param(self, qparam):
        result = self._get_query_param(qparam)
        try:
            return int(result)
        except ValueError:
            rh_logger.logger.report_event(
                "Received REST API call with non-integer %s: %s" %
                (qparam, result))
            raise HTTPError(
                self.request.uri, 400,
                "The %s query parameter must be an integer, but was %s" %
                (qparam, result), [], None)

    def get_data(self):
        channel = self._get_channel_config()
        x = self._get_int_query_param(self.Q_X)
        y = self._get_int_query_param(self.Q_Y)
        z = self._get_int_query_param(self.Q_Z)
        width = self._get_int_query_param(self.Q_WIDTH)
        height = self._get_int_query_param(self.Q_HEIGHT)
        resolution = self.get_query_argument(self.Q_RESOLUTION, 0)
        fmt = self.get_query_argument(self.Q_FORMAT, "png")
        if fmt not in settings.SUPPORTED_IMAGE_FORMATS:
            rh_logger.logger.report_event(
                "Received unsupported %s query parameter: " + fmt)
            raise HTTPError(
                self.request.uri, 400,
                "The %s query parameter must be one of \"%s\"." %
                (self.Q_FORMAT, '","'.join(settings.SUPPORTED_IMAGE_FORMATS)),
                [], None)
        try:
            resolution = int(resolution)
        except ValueError:
            rh_logger.logger.report_event(
                "Received REST API call with non-integer %s: %s" %
                (self.Q_RESOLUTION, resolution))
            raise HTTPError(
                self.request.uri, 400,
                "The %s query parameter must be an integer, but was %s" %
                (self.Q_RESOLUTION, resolution), [], None)
        dtype = getattr(np, channel[self.DATA_TYPE])
        rh_logger.logger.report_event(
            "Encoding image as dtype %s" % repr(dtype))
        vol = self.core.get(channel[self.PATH],
                            [x, y, z], [width, height, 1],
                            w=resolution, dtype=dtype)
	cropped = vol[:height, :width, 0].astype(dtype)
	if dtype is np.uint32:
            cropped = cropped.view(np.uint8).reshape(cropped.shape+(4,))[:,:,:3]
        data = cv2.imencode(  "." + fmt, cropped)[1]
        self.set_header("Content-Type", "image/"+fmt)
        self.write(data.tostring())

    def get_mask(self):
        # TODO: implement this
        raise HTTPError(self.request.uri, 501,
                        "The server does not yet support /api/mask requests",
                        [], None)
