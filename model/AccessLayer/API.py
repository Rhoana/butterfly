from Query import Query
from Settings import *
from RequestHandler import RequestHandler

class API(RequestHandler):

    def parse(self, request):

        whois = self.request.remote_ip
        settings = {
            'feature': whois
        }
        return Query(**settings)

    def _get_config(self,kind):
        # Get the config dictionary for a named kind
        target = self._get_necessary_param(kind['param'])
        for d in kind['parent'].get(kind['plural'],[]):
            if d[self.NAME] == target:
                return d
        else:
            msg = 'Unknown '+kind['name']+': '+ target
            rh_logger.logger.report_event(msg)
            raise HTTPError(self.request.uri, 400, msg, [], None)

    def get_experiments(self):
        # Handle the /api/experiments GET request
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
        # Handle the /api/samples GET request
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
        # Handle the /api/datasets GET request
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
        # Handle the /api/channels GET request
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
        # Handle the /api/channel_metadata GET request
        return self._get_channel_config().copy()

    def _except(self,result,kwargs):
        action = 'exist'
        if 'check' in kwargs:
            kwargs['val'] = result
            action = 'check'
        message = self.log(action, kwargs)
        raise HTTPError(self.request.uri, 400, message, [], None)

    def _match_condition(self,result,checked,kwargs):
        if checked: self._except(result, kwargs)
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
        return self._match_condition(result, result not in whitelist, {
            'check' : 'in '+' '.join(whitelist),
            'term' : qparam
        })

    def _get_necessary_param(self, qparam):
        result = self.get_query_argument(qparam, default=None)
        return self._match_condition(result, result is None, {
            'term': qparam
        })

    def _get_int_necessary_param(self, qparam):
        result = self._get_necessary_param(qparam)
        return self._try_typecast_int(qparam, result)

    def _get_int_query_argument(self, qparam):
        result = self.get_query_argument(qparam, 0)
        return self._try_typecast_int(qparam, result)

    def get_data(self):
        channel = self._get_channel_config()
        x = self._get_int_necessary_param(self.Q_X)
        y = self._get_int_necessary_param(self.Q_Y)
        z = self._get_int_necessary_param(self.Q_Z)
        width = self._get_int_necessary_param(self.Q_WIDTH)
        height = self._get_int_necessary_param(self.Q_HEIGHT)
        resolution = self._get_int_query_argument(self.Q_RESOLUTION)
        fmt = self._get_list_query_argument(self.Q_FORMAT, settings.SUPPORTED_IMAGE_FORMATS)
        view = self._get_list_query_argument(self.Q_VIEW, settings.SUPPORTED_IMAGE_VIEWS)

        dtype = getattr(np, channel[self.DATA_TYPE])
        slice_define = [channel[self.PATH], [x, y, z], [width, height, 1]]
        rh_logger.logger.report_event("Encoding image as dtype %s" % repr(dtype))
        vol = self.core.get(*slice_define, w=resolution, dtype=dtype, view=view)
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
