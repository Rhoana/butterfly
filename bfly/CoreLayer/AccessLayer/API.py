from RequestHandler import RequestHandler
from QueryLayer import InfoQuery
from QueryLayer import DataQuery
from urllib2 import URLError
import numpy as np

class API(RequestHandler):
    """ Responds to :data:`bfly.Webserver._webapp` /api endpoint

    Attributes
    -----------
    inherits: :class:`RequestHandler`


    :h:`Methods`

    """
    def parse(self, request):
        """ Extract details from any of the methods
        Overrides :meth:`Database.parse`

        Calls :meth:`_meta_info`, :meth:`_feature_info`, \
:meth:`_get_group`, or :meth:`_get_data` to return \
an :class:`InfoQuery` or :class:`DataQuery` as a \
response to the given ``method``

        Arguments
        ----------
        request: str
            The single method requested in the URL

        Returns
        ---------
        :class:`QueryLayer.Query`
            contains standard details for each request
        """

        super(API, self).parse(request)

        meths = self.INPUT.METHODS.LIST
        command = self._match_list('method', request, meths)

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

    @property
    def _meta_info(self):
        """ Loads :class:`InfoQuery` for ``INPUT.METHODS.META``

        Returns
        --------
        :class:`InfoQuery`
            made with info from :meth:`_get_group_dict`
        """
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
        """ Loads :class:`InfoQuery` for ``INPUT.METHODS.FEATURE``

        Returns
        --------
        :class:`InfoQuery`
            with a feature passed as `OUTPUT.INFO.NAMES` \
from :meth:`_id_feature` or :meth:`_box_feature`
        """
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
        """ Get the table and key for feature request

        Arguments
        ----------
        feat : str
            The name of the feature requested

        Returns
        ---------
        :class:`Database`
            a reference to :data:`_db`
        str
            the name of the table for the feature
        str
            the primary key for the table
        """
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

    def _id_feature(self, feat, path, id_key):
        """ Loads a feature list that needs an id

        Calls :meth:`_db_feature` to access database

        Arguments
        -----------
        feat : str
            The name of the feature request
        path : str
            The path to the corresponding image data
        id_key : int
            The key value for a :class:`Database` table

        Returns
        --------
        list or dict
            The feature used to make an :class:`InfoQuery`
        """

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
            post_result = db.get_entry(db_table, path, **{
                k_nodes[0]: id_key
            })
            pre_result = db.get_entry(db_table, path, **{
                k_nodes[1]: id_key
            })
            all_results = {}
            ## Format them in a dictionary
            for pre in pre_result:
                all_results[pre[db_key]] = 1
            for post in post_result:
                all_results[post[db_key]] = 2
            # return pre and post results
            return all_results

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
        """ Loads a feature list that needs a bounding box

        Calls :meth:`_db_feature` to access database

        Arguments
        -----------
        feat : str
            The name of the feature request
        path : str
            The path to the corresponding image data
        bounds : list
            The 6-item list of a volume origin and shape

        Returns
        --------
        list or dict
            The feature used to make an :class:`InfoQuery`
        """

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

    #####
    #Lists values from config for group methods
    #####

    def get_value(self, g):
        """ get the name of a group

        Arguments
        ----------
        g: dict
            The group from :data:`BFLY_CONFIG`

        Returns
        --------
        str
            the name of `g`
        """
        return g.get(self.INPUT.GROUP.NAME,'')

    def _find_all_groups(self, _method):
        """ Pairs all groups needed for the ``_method``

        Arguments
        ----------
        _method: str
            The name of the group method requested

        Returns
        --------
        list
            list of pairs of group query terms and values
        """
        group_methods = self.INPUT.METHODS.GROUP_LIST
        group_queries = self.INPUT.GROUP.LIST
        # List all parent methods of _method
        if _method in group_methods:
            group_index = group_methods.index(_method)
            group_methods = group_methods[:group_index]
            group_queries = group_queries[:group_index]

        return zip(group_methods, group_queries)

    def _get_group_dict(self, _method):
        """ get the config dictionary for the requested method

        Arguments
        ----------
        _method: str
            The name of the method requesting group information

        Returns
        --------
        dict
            The requested sub-dictionary from :data:`BFLY_CONFIG`
        """
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
        """ Make :class:`InfoQuery` for groups in the requested group

        Arguments
        ----------
        _method: str
            The name of the method requesting group information

        Returns
        --------
        :class:`InfoQuery`
            The :data:`OUTPUT.INFO` ``.NAMES.NAME`` keyword \
has the list of groups in the requested group from \
:meth:`_get_group_dict`
        """
        out_format = self._get_list_query(self.INPUT.INFO.FORMAT)
        group_list = self._get_group_dict(_method).get(_method,[])
        group_values = map(self.get_value, group_list)

        # Return an empty query
        return InfoQuery(**{
            self.INPUT.METHODS.NAME: _method,
            self.INPUT.INFO.FORMAT.NAME: out_format,
            self.OUTPUT.INFO.NAMES.NAME: group_values
        })

    #####
    #Loads data from tiles for image methods
    #####

    def get_data(self, _method):
        """ Make :class:`DataQuery` for an image at request path

        Arguments
        ----------
        _method: str
            The name of the method requesting image information

        Returns
        --------
        :class:`DataQuery`
            The :data:`OUTPUT.INFO` ``.Path.NAME`` keyword \
has the path to data in the requested group from \
:meth:`_get_group_dict`
        """
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

    ####
    # Handles Logs and Exceptions
    ####

    def _except(self, result, detail):
        """ raises a 400 URLError for logging

        Arguments
        ----------
        result: anything
            the failed ``result`` value
        detail: dict
            * :data:`RUNTIME` ``.ERROR.CHECK.NAME`` \
(str) -- description of failure
            * :data:`RUNTIME` ``.ERROR.TERM.NAME`` \
(str) -- the failed property name

        Raises
        -------
        URLError
            Contains all ``detail`` needed for log
        """
        k_out = self.RUNTIME.ERROR.OUT.NAME
        detail[k_out] = result
        raise URLError(['CHECK', 400, detail])

    def _match_condition(self, result, checked, detail):
        """ Calls :meth:`_except` given condition is false

        Arguments
        -----------
        result: anything
            The value checked in the ``checked`` condition
        checked: bool
            Raises an exception if false
        detail: dict
            * :data:`RUNTIME` ``.ERROR.CHECK.NAME`` \
(str) -- description of possible failure
            * :data:`RUNTIME` ``.ERROR.TERM.NAME`` \
(str) -- the name of ``result`` property

        Returns
        --------
        anything:
            The ``result`` value if ``checked`` true
        """
        if not checked: self._except(result, detail)
        return result

    def _try_condition(self, result, check, detail):
        """ Calls :meth:`_except` if a function fails to run

        Arguments
        -----------
        result: anything
            The value to pass to the ``checked`` function
        checked: callable
            The function to try to call on ``result``
        detail: dict
            * :data:`RUNTIME` ``.ERROR.CHECK.NAME`` \
(str) -- description of possible failure
            * :data:`RUNTIME` ``.ERROR.TERM.NAME`` \
(str) -- the name of ``result`` property

        Returns
        --------
        anything:
            The ``result`` value if ``checked`` returns
        """
        try: return check(result)
        # Except main errors for known checks
        except (TypeError, ValueError):
            self._except(result, detail)

    def _try_typecast_int(self, qparam, result):
        """ Try to convert a query result to an integer

        Arguments
        -----------
        qparam: str
            The name of the ``result`` property
        result: anything
            The value to try to convert to ``numpy.uint32``

        Returns
        ---------
        numpy.uint32
            If the ``result`` can convert to an integer
        """
        k_term = self.RUNTIME.ERROR.TERM.NAME
        k_check = self.RUNTIME.ERROR.CHECK.NAME
        return self._try_condition(result, np.uint32, {
            k_check : 'a number',
            k_term : qparam
        })

    def _match_list(self, name, result, whitelist):
        """ Try to convert a query result to an integer

        Arguments
        -----------
        name: str
            The name of the ``result`` property
        result: anything
            The value to check for in the ``whitelist``
        whitelist: list
            The list of all accepted ``result``

        Returns
        ---------
        anything
            If the ``result`` is in the ``whitelist``
        """
        k_term = self.RUNTIME.ERROR.TERM.NAME
        k_check = self.RUNTIME.ERROR.CHECK.NAME
        # Check if the result is in the list
        in_list = result in whitelist
        return self._match_condition(result, in_list, {
            k_check : 'one of {}'.format(whitelist),
            k_term : name
        })

    def _get_list_query(self, field):
        """ Call :meth:`_match_list` for a given structure

        Get a ``result`` from the URL parameter for the ``field``\
using :meth:`get_query_argument`

        Arguments
        ----------
        field: :class:`NamedStruct`
            * NAME (str) -- the name of the property
            * VALUE (anything) -- the default property value
            * LIST (list) -- the list of valid property values

        Returns
        ---------
        anything
            If the ``result`` is in the ``field.LIST``
        """
        result = self.get_query_argument(field.NAME, field.VALUE)
        return self._match_list(field.NAME, result, field.LIST)

    def _get_int_query(self, field):
        """ Call :meth:`_try_typecast_int` for a structure

        Get a ``result`` from the URL parameter for the ``field``\
using :meth:`get_query_argument`

        Arguments
        ----------
        field: :class:`NamedStruct`
            * NAME (str) -- the name of the property
            * VALUE (anything) -- the default property value

        Returns
        ---------
        np.uint32
            If the ``result`` can be converted to an integer
        """
        result = self.get_query_argument(field.NAME, field.VALUE)
        return self._try_typecast_int(field.NAME, result)
