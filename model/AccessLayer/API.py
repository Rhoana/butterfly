from RequestHandler import RequestHandler
from QueryLayer import InfoQuery
from QueryLayer import DataQuery
from urllib2 import HTTPError
from Settings import *

class API(RequestHandler):

    RANKINGS = RANKINGS
    NAME = INFOTERMS[0]
    LIST = INFOTERMS[2]
    METHOD = INFOTERMS[1]
    FORMAT = TILETERMS[0]
    DATAMETHODS = DATAMETHODS
    METHODS = METHODS

    def parse(self, command):
        metamethods = self.METHODS + self.RANKINGS
        if command in metamethods:
            return self._get_list(command)
        if command in self.DATAMETHODS:
            return self.get_data()

        all_methods = metamethods + self.DATAMETHODS
        return self._match_condition(command, False, {
            'check' : 'one of ['+', '.join(all_methods)+']',
            'term' : 'command'
        })

    def _get_ask(self, _method, _list):
        param = GROUPINGS.get(_method,'')
        return self._get_list_query_argument(param,_list,'')

    def _find_terms(self, _raw_terms):
        if _raw_terms[self.METHOD] in self.METHODS:
            _raw_terms[self.LIST] = ['not yet']
        return _raw_terms

    def _get_list(self, _method):
        n_meth = -1
        raw_terms = {
            self.METHOD: _method,
            self.FORMAT: 'json'
        }
        features = bfly_config.copy()
        get_name = lambda g: g.get(self.NAME,'')
        # List needed methods to find asked _method
        if _method in self.RANKINGS:
            n_meth = self.RANKINGS.index(_method)
        needed = self.RANKINGS[:n_meth]
        # Find all needed groups as asked
        for need in needed:
            # Find the value of method needed
            grouplist = features.get(need,[])
            groupnames = map(get_name, grouplist)
            ask = self._get_ask(need, groupnames)
            raw_terms[need] = ask
            # Find group matching name in list of groups 
            features = grouplist[groupnames.index(ask)]
        # Get list of method groups from parent features group
        raw_terms.update(features)
        result_list = features.get(_method, [])
        raw_terms[self.LIST] = map(get_name, result_list)
        terms = self._find_terms(raw_terms)
        print terms[self.LIST]
        return InfoQuery(**terms)

    def _except(self,result,kwargs):
        action = 'exist'
        if 'check' in kwargs:
            kwargs['val'] = result
            action = 'check'
        message = self.log(action, **kwargs)
        raise HTTPError(self.request.uri, 400, message, [], None)

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

    def _get_list_query_argument(self, qparam, whitelist, _default):
        result = self.get_query_argument(qparam, _default)
        return self._match_condition(result, result in whitelist, {
            'check' : 'one of ['+', '.join(whitelist)+']',
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
        channel = self._get_list(self.RANKINGS[-1])
        x = self._get_int_necessary_param(self.x)
        y = self._get_int_necessary_param(self.y)
        z = self._get_int_necessary_param(self.z)
        width = self._get_int_necessary_param(self.width)
        height = self._get_int_necessary_param(self.height)
        resolution = self._get_int_query_argument(self.resolution)
        fmt = self._get_list_query_argument(*FORMAT_LIST)
        view = self._get_list_query_argument(*VIEW_LIST)

        testing = {
            'method': 'data',
            'resolution': resolution,
            'height': height,
            'width': width,
            'format': fmt,
            'view': view,
            'x': x,
            'y': y,
            'z': z
        }

        return DataQuery(**testing)

        slice_define = [channel[self.PATH], [x, y, z], [width, height, 1]]
        vol = self._core.get(*slice_define, w=resolution, view=view)
        self.set_header("Content-Type", "image/"+fmt)
        if fmt in ['zip']:
            output = StringIO.StringIO()
            volstring = vol.tostring('F')
            output.write(zlib.compress(volstring))
            content = output.getvalue()
        else:
            content = cv2.imencode(  "." + fmt, vol)[1].tostring()

        self.write(content)

    def get_mask(self):
        # TODO: implement this
        msg ="The server does not yet support /api/mask requests"
        raise HTTPError(self.request.uri, 501, msg, [], None)
