from RequestHandler import RequestHandler
from QueryLayer import InfoQuery
from QueryLayer import DataQuery
from urllib2 import HTTPError

class API(RequestHandler):

    def parse(self, *args):
        meth = str(args[0])
        meths = self.INPUT.METHODS.LIST
        command = self._check_list('method',meth,meths)

        if command in self.INPUT.METHODS.INFO_LIST:
            return self._get_list(command)
        if command in self.INPUT.METHODS.GROUP_LIST:
            return self._get_list(command)
        if command in self.INPUT.METHODS.IMAGE_LIST:
            return self.get_data(command)

        return 'Unsupported Request Category'

    def _add_info_terms(self, _terms):
        list_name = self.OUTPUT.INFO.NAMES.NAME
        _terms[list_name] = ['not yet']
        return _terms

    def _find_terms(self, _terms):
        method = _terms[self.INPUT.METHODS.NAME]
        info_methods = self.INPUT.METHODS.INFO_LIST
        if method == info_methods[1]:
            _terms = self._add_info_terms(_terms)
        return _terms

    def _get_list(self, _method):
        format_list = self.INPUT.INFO.FORMAT
        output = self._get_list_query(format_list)
        raw_terms = {
            self.INPUT.METHODS.NAME: _method,
            self.OUTPUT.INFO.SIZE.NAME: {},
            format_list.NAME: output
        }
        features = self.BFLY_CONFIG
        need_term = self.INPUT.GROUP_LIST
        need_meth = self.INPUT.METHODS.GROUP_LIST
        name_name = self.OUTPUT.INFO.CHANNEL.NAME
        get_name = lambda g: g.get(name_name,'')
        # List needed methods to find asked _method
        if _method in need_meth:
            n_meth = need_meth.index(_method)
            need_meth = need_meth[:n_meth]
            need_term = need_term[:n_meth]
        # Find all needed groups as asked
        for nmeth,nterm in zip(need_meth,need_term):
            # Find the value of method needed
            grouplist = features.get(nmeth,[])
            groupnames = map(get_name, grouplist)
            ask = self.get_query_argument(nterm, '')
            ask = self._check_list(nterm,ask,groupnames)
            raw_terms[nterm] = ask
            # Find group matching name in list of groups 
            features = grouplist[groupnames.index(ask)]
        # Get list of method groups from parent features group
        raw_terms.update(features)
        result_list = features.get(_method, [])
        list_name = self.OUTPUT.INFO.NAMES.NAME
        raw_terms[list_name] = map(get_name, result_list)
        terms = self._find_terms(raw_terms)
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

    def _check_list(self,name,v,vlist):
        return self._match_condition(v, v in vlist, {
            'check' : 'one of ['+', '.join(vlist)+']',
            'term' : name
        })

    def _get_list_query(self, _query_list):
        q_name = _query_list.NAME
        default = _query_list.VALUE
        whitelist = _query_list.LIST
        result = self.get_query_argument(q_name, default)
        return self._check_list(q_name,result,whitelist)

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

    def get_data(self, method):
        # First validate group terms in query
        info_methods = self.INPUT.METHODS.INFO_LIST
        info_query = self._get_list(info_methods[0])
        all_res = self.INPUT.RESOLUTION.XY.NAME
        resolution = self._get_int_query_argument(all_res)
        form = self._get_list_query(self.INPUT.IMAGE.FORMAT)
        view = self._get_list_query(self.INPUT.IMAGE.VIEW)
        terms = {
            all_res: resolution,
            self.INPUT.METHODS.NAME: method,
            self.INPUT.IMAGE.FORMAT.NAME: form,
            self.INPUT.IMAGE.VIEW.NAME: view
        }
        path_name = self.OUTPUT.INFO.PATH.NAME
        terms[path_name] = info_query.OUTPUT.INFO.PATH.VALUE

        for k in self.INPUT.ORIGIN_LIST:
            terms[k] = self._get_int_necessary_param(k)
        for k in self.INPUT.SHAPE_LIST:
            terms[k] = self._get_int_necessary_param(k)

        return DataQuery(**terms)

    def get_mask(self):
        # TODO: implement this
        msg ="The server does not yet support /api/mask requests"
        raise HTTPError(self.request.uri, 501, msg, [], None)
