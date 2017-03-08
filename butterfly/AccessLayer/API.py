from RequestHandler import RequestHandler
from QueryLayer import InfoQuery
from QueryLayer import DataQuery
from urllib2 import URLError
import numpy as np

class API(RequestHandler):

    def parse(self, request):

        super(API, self).parse(request)

        meths = self.INPUT.METHODS.LIST
        command = self._match_list('method',request,meths)

        if command == self.INPUT.METHODS.META.NAME:
            return self._get_meta_info()
        if command == self.INPUT.METHODS.FEAT.NAME:
            return self._get_feature_info()
        # Handle all methods the same if in same list
        if command in self.INPUT.METHODS.GROUP_LIST:
            return self._get_group(command)
        if command in self.INPUT.METHODS.IMAGE_LIST:
            return self.get_data(command)

        return 'Unsupported Request Category'

    '''
    Loads dictionary for info methods
    '''

    def _get_meta_info(self):
        # Get needed metadata
        info = self.OUTPUT.INFO
        in_info = self.INPUT.INFO
        methods = self.INPUT.METHODS
        # Get all the channel info
        meta_info = self._get_group_dict('')

        # The input format becomes the output format
        out_format = self._get_list_query(in_info.FORMAT)

        return InfoQuery(**{
            info.CHANNEL.NAME: meta_info[info.CHANNEL.NAME],
            info.PATH.NAME: meta_info[info.PATH.NAME],
            methods.NAME: methods.META.NAME,
            in_info.FORMAT.NAME: out_format
        })

    def _get_feature_info(self):
        # Get needed metadata
        info = self.OUTPUT.INFO
        in_info = self.INPUT.INFO
        methods = self.INPUT.METHODS
        features = self.INPUT.FEATURES
        # Get all the channel info
        meta_info = self._get_group_dict('')

        # The input format becomes the output format
        out_format = self._get_list_query(in_info.FORMAT)
        # Get the name of the feature to load from db
        feature_key = self._get_list_query(features)

        # Make an empty output list
        output_list = [feature_key]

        return InfoQuery(**{
            info.PATH.NAME: meta_info[info.PATH.NAME],
            methods.NAME: methods.FEAT.NAME,
            in_info.FORMAT.NAME: out_format,
            info.NAMES.NAME: output_list
        })

    '''
    Lists values from config for group methods
    '''

    def get_value(self, g):
        return g.get(self.INPUT.GROUP.NAME,'')

    def _find_all_groups(self, _method):
        group_methods = self.INPUT.METHODS.GROUP_LIST
        group_queries = self.INPUT.GROUP.LIST
        # List all parent methods of _method
        if _method in group_methods:
            group_index = group_methods.index(_method)
            group_methods = group_methods[:group_index]
            group_queries = group_queries[:group_index]

        return zip(group_methods, group_queries)

    def _get_group_dict(self, _method):
        configured = self.BFLY_CONFIG
        # validate each query value in each configured level
        for method, query in self._find_all_groups(_method):
            valid_groups = configured.get(method,[])
            valid_values = map(self.get_value, valid_groups)
            # Check query value against all valid query values
            query_value = self.get_query_argument(query,'')
            self._match_list(query, query_value, valid_values)
            # Continue matching query_value from list of valid groups
            configured = valid_groups[valid_values.index(query_value)]
        return configured

    def _get_group(self, _method):
        out_format = self._get_list_query(self.INPUT.INFO.FORMAT)
        group_list = self._get_group_dict(_method).get(_method,[])
        group_values = map(self.get_value, group_list)

        # Return an empty query
        return InfoQuery(**{
            self.INPUT.METHODS.NAME: _method,
            self.INPUT.INFO.FORMAT.NAME: out_format,
            self.OUTPUT.INFO.NAMES.NAME: group_values
        })

    '''
    Loads data from tiles for image methods
    '''

    def get_data(self, _method):
        # Parse all the group terms
        meta_dict = self._get_group_dict('')
        path_key = self.OUTPUT.INFO.PATH.NAME

        # Begin building needed keywords
        terms = {path_key: meta_dict[path_key]}
        terms[self.INPUT.METHODS.NAME] = _method

        # get terms from IMAGE
        for key in ['VIEW','FORMAT']:
            term = getattr(self.INPUT.IMAGE, key)
            terms[term.NAME] = self._get_list_query(term)

        # get integers from POSITION
        for key in ['X','Y','Z','WIDTH','HEIGHT','DEPTH']:
            term = getattr(self.INPUT.POSITION, key)
            terms[term.NAME] = self._get_int_query(term)

        # get integers from RESOLUTION
        term = getattr(self.INPUT.RESOLUTION, 'XY')
        terms[term.NAME] = self._get_int_query(term)

        return DataQuery(**terms)

    '''
    Handles Logs and Exceptions
    '''

    def _except(self,result,detail):
        k_out = self.RUNTIME.ERROR.OUT.NAME
        detail[k_out] = result
        raise URLError({
            'error': 'bad_check',
            'keys': detail,
            'http': '400'
        })

    def _match_condition(self,result,checked,kwargs):
        if not checked: self._except(result, kwargs)
        return result

    def _try_condition(self,result,check,kwargs):
        try: return check(result)
        except: self._except(result, kwargs)

    def _try_typecast_int(self,qparam,result):
        k_term = self.RUNTIME.ERROR.TERM.NAME
        k_check = self.RUNTIME.ERROR.CHECK.NAME
        return self._try_condition(result, np.uint32, {
            k_check : 'a number',
            k_term : qparam
        })

    def _match_list(self,name,v,vlist):
        k_term = self.RUNTIME.ERROR.TERM.NAME
        k_check = self.RUNTIME.ERROR.CHECK.NAME
        return self._match_condition(v, v in vlist, {
            k_check : 'one of {}'.format(vlist),
            k_term : name
        })

    def _get_list_query(self, _query):
        result = self.get_query_argument(_query.NAME, _query.VALUE)
        return self._match_list(_query.NAME,result,_query.LIST)

    def _get_int_query(self, _query):
        result = self.get_query_argument(_query.NAME, _query.VALUE)
        return self._try_typecast_int(_query.NAME, result)

