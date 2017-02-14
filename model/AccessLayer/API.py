from RequestHandler import RequestHandler
from Query import Query
from Settings import *

class API(RequestHandler):

    '''Encode image/mask in this image format (e.g. "tif")'''
    Q_X = "x"
    Q_Y = "y"
    Q_Z = "z"
    Q_VIEW = "view"
    Q_WIDTH = "width"
    Q_HEIGHT = "height"
    Q_FORMAT = "format"
    Q_RESOLUTION = "resolution"

    # Query params for grouping
    Q_EXPERIMENT = "experiment"
    EXPERIMENTS = "experiments"
    Q_SAMPLE = "sample"
    SAMPLES = "samples"
    Q_DATASET = "dataset"
    DATASETS = "datasets"
    Q_CHANNEL = "channel"
    CHANNELS = "channels"

    GROUPINGS = {
        EXPERIMENTS: Q_EXPERIMENT,
        SAMPLES: Q_SAMPLE,
        DATASETS: Q_DATASET,
        CHANNELS: Q_CHANNEL
    }
    METADATA = 'channel_metadata'
    RANKINGS = [EXPERIMENTS, SAMPLES, DATASETS]
    RANKINGS = RANKINGS + [CHANNELS, METADATA]

    NAME = "name"
    PATH = "path"
    DATA_TYPE = "data-type"
    DIMENSIONS = "dimensions"
    SHORT_DESCRIPTION = "short-description"

    def parse(self, command):
        if command in self.RANKINGS:
            print command
            return self._get_list(command)
        whois = self.request.remote_ip
        return self.get_data()

    def _get_ask(self, _method):
        param = self.GROUPINGS.get(_method,{})
        return self._get_necessary_param(param)

    def _get_list(self, _method):
        features = bfly_config.copy()
        get_name = lambda g: g.get(self.NAME,'')
        # List needed methods to find asked _method
        needed = self.RANKINGS[:self.RANKINGS.index(_method)]
        # Find the values of methods needed by request
        asking = map(self._get_ask, needed)
        # Find all needed groups as asked
        for need,ask in zip(needed, asking):
            grouplist = features.get(need,[])
            # Find group matching name in list of groups 
            ask_name = lambda g: get_name(g) == ask
            features = next(filter(ask_name, grouplist),{})
        # Get list of method groups from parent features group
        results = features.get(_method, 0)
        raw = map(get_name, results) if results else features
        return Query(view=raw)

    def get_experiments(self):
        return self._get_list(self.EXPERIMENTS)

    def get_samples(self):
        return self._get_list(self.SAMPLES)

    def get_datasets(self):
        return self._get_list(self.DATASETS)

    def get_channels(self):
        return self._get_list(self.CHANNELS)

    def get_channel_metadata(self):
        return self._get_list(self.METADATA)

    def _except(self,result,kwargs):
        action = 'exist'
        if 'check' in kwargs:
            kwargs['val'] = result
            action = 'check'
        message = self.log(action, **kwargs)
        #raise HTTPError(self.request.uri, 400, message, [], None)

    def _match_condition(self,result,checked,kwargs):
        if not checked: self._except(result, kwargs)
        return result

    def _try_condition(self,result,check,kwargs):
        try: return check(result)
        except: self._except(result, kwargs)

    def _try_typecast_int(self,qparam,result):
        return self._try_condition(result, int, {
            'check' : 'a number',
            'term' : qparam
        })

    def _get_list_query_argument(self, qparam, whitelist):
        result = self.get_query_argument(qparam, whitelist[0])
        return self._match_condition(result, result in whitelist, {
            'check' : 'in '+' '.join(whitelist),
            'term' : qparam
        })

    def _get_necessary_param(self, qparam):
        result = self.get_query_argument(qparam, default=None)
        return self._match_condition(result, result is not None, {
            'term': qparam
        })

    def _get_int_necessary_param(self, qparam):
        result = self._get_necessary_param(qparam)
        return self._try_typecast_int(qparam, result)

    def _get_int_query_argument(self, qparam):
        result = self.get_query_argument(qparam, 0)
        return self._try_typecast_int(qparam, result)

    def get_data(self):
        #channel = self.get_channel_metadata()
        x = self._get_int_necessary_param(self.Q_X)
        y = self._get_int_necessary_param(self.Q_Y)
        z = self._get_int_necessary_param(self.Q_Z)
        width = self._get_int_necessary_param(self.Q_WIDTH)
        height = self._get_int_necessary_param(self.Q_HEIGHT)
        resolution = self._get_int_query_argument(self.Q_RESOLUTION)
        fmt = self._get_list_query_argument(self.Q_FORMAT, SUPPORTED_IMAGE_FORMATS)
        view = self._get_list_query_argument(self.Q_VIEW, SUPPORTED_IMAGE_VIEWS)
        fmt = 'json'
        testing = {
            'resolution': resolution,
            'channel': 'channel',
            'height': height,
            'width': width,
            'format': fmt,
            'view': view,
            'x': x,
            'y': y,
            'z': z
        }

        return Query(**testing)

        dtype = getattr(np, channel[self.DATA_TYPE])
        slice_define = [channel[self.PATH], [x, y, z], [width, height, 1]]
        rh_logger.logger.report_event("Encoding image as dtype %s" % repr(dtype))
        vol = self._core.get(*slice_define, w=resolution, dtype=dtype, view=view)
        self.set_header("Content-Type", "image/"+fmt)
        if fmt in ['zip']:
            output = StringIO.StringIO()
            volstring = vol.transpose(1,0,2).astype(np.uint32).tostring('F')
            output.write(zlib.compress(volstring))
            content = output.getvalue()
        else:
            content = cv2.imencode(  "." + fmt, vol)[1].tostring()

        self.write(content)

    def get_mask(self):
        # TODO: implement this
        msg ="The server does not yet support /api/mask requests"
        raise HTTPError(self.request.uri, 501, msg, [], None)



