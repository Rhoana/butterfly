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
            return self._meta_info
        if command == self.INPUT.METHODS.FEAT.NAME:
            return self._feature_info
        # Handle all methods the same if in same list
        if command in self.INPUT.METHODS.GROUP_LIST:
            return self._get_group(command)
        if command in self.INPUT.METHODS.IMAGE_LIST:
            return self.get_data(command)

        return 'Unsupported Request Category'

    '''
    Loads dictionary for info methods
    '''

    @property
    def _meta_info(self):
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

    @property
    def _feature_info(self):
        # Get needed metadata
        info = self.OUTPUT.INFO
        in_info = self.INPUT.INFO
        methods = self.INPUT.METHODS
        feats = self.INPUT.FEATURES
        # Create empty parameters
        id_key = None
        bounds = []

        # Get all the channel info
        meta_info = self._get_group_dict('')
        # The path and the  output format
        path = meta_info[info.PATH.NAME]
        out_format = self._get_list_query(in_info.FORMAT)
        # Get the name of the feature to load from db
        feat = self._get_list_query(feats)

        # All features that need id
        if feat not in feats.LABEL_LIST:
            id_key = self._get_int_query(in_info.ID)
            # Return feature based on id
            feature = self._id_feature(feat, path, id_key)
        # All features that need bounds
        else:
            # get bounds from input
            for key in ['Z','Y','X','DEPTH','HEIGHT','WIDTH']:
                term = getattr(self.INPUT.POSITION, key)
                bounds.append(self._get_int_query(term))
            # Return feature based on bounds
            feature = self._box_feature(feat, path, bounds)

        # Return an infoquery
        return InfoQuery(**{
            methods.NAME: methods.FEAT.NAME,
            in_info.FORMAT.NAME: out_format,
            info.NAMES.NAME: feature,
            info.PATH.NAME: path
        })

    # Get the db table and key
    def _db_feature(self, feat):
        # Get all keywords
        feats = self.INPUT.FEATURES
        k_tables = self.RUNTIME.DB.TABLE

        # List all the tables in the database
        db_list = map(feats.TABLES.get, k_tables.LIST)
        # Get the table that handles given request
        in_db = (f.NAME for f in db_list if feat in f.LIST)
        db_table = next(in_db, '')

        # return empty
        if not db_table:
            return self._db, db_table, 0

        # Find the primary key for the table
        db_key = k_tables[db_table].KEY.NAME
        # Return database, table, and key
        return self._db, db_table, db_key

    # Get all features that need an id
    def _id_feature(self, feat, path, id_key):
        # Get input keyword arguments
        feats = self.INPUT.FEATURES
        # Get metadata for database
        k_tables = self.RUNTIME.DB.TABLE
        k_nodes = k_tables.SYNAPSE.NEURON_LIST
        k_z,k_y,k_x = k_tables.ALL.POINT_LIST
        # Get output keyword arguments
        k_links = self.OUTPUT.FEATURES.LINKS

        # Shorthand database name, table, key
        db, db_table, db_key = self._db_feature(feat)

        # Do not have
        if not db_table:
            return ['Voxel List not Supported yet']

        # Find all synapses where neuron is parent
        if feat == feats.NEURON_CHILDREN.NAME:
            result = db.get_entry(db_table, path, **{
                k_nodes[0]: id_key
            })
            return [ s[db_key] for s in result ]

        # Just look at one result with the ID
        result = db.get_entry(db_table, path, id_key)

        # Only first result needed
        if result and isinstance(result, list):
            result = result[0]

        # Just check record of an ID
        if feat in feats.BOOL_LIST:
            return not not result

        # Empty features
        if not result:
            return {}

        # If the request gets a keypoint
        if feat in feats.POINT_LIST:
            return {
                k_z: result[k_z],
                k_y: result[k_y],
                k_x: result[k_x]
            }

        # If the request asks for all links
        if feat == feats.SYNAPSE_LINKS.NAME:
            return {
                k_links.ID.NAME: result[db_key],
                k_links.PRE.NAME: result[k_nodes[0]],
                k_links.POST.NAME: result[k_nodes[1]]
            }

        # Not yet supported
        return [db_table]

    # Get all features that need bounds
    def _box_feature(self, feat, path, bounds):
        # Get input keyword arguments
        feats = self.INPUT.FEATURES
        # Get metadata for database
        k_tables = self.RUNTIME.DB.TABLE
        k_z,k_y,k_x = k_tables.ALL.POINT_LIST

        # Shorthand database name, table, key
        db, db_table, db_key = self._db_feature(feat)

        # Get start and end of bounds
        start = np.uint32(bounds[:3])
        end = start + bounds[3:]

        # Bound center in start and end
        def bounded(s):
            c = map(s.get, [k_z,k_y,k_x])
            return all(c > start) and all(c < end)

        # Do not know
        if not db_table:
            return ['Feature not understood']

        # if request for labels in bounds
        if feat in feats.LABEL_LIST:
            # Find the center points within the bounds
            result = db.get_entry(db_table, path, bounded)
            return [ s[db_key] for s in result ]

        # Not yet supported
        return [db_table]

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
        for key in ['Z','Y','X','DEPTH','HEIGHT','WIDTH']:
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
        raise URLError(['CHECK', 400, detail])

    def _match_condition(self,result,checked,kwargs):
        if not checked: self._except(result, kwargs)
        return result

    def _try_condition(self,result,check,kwargs):
        try: return check(result)
        # Except main errors for known checks
        except (TypeError, ValueError):
            self._except(result, kwargs)

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

