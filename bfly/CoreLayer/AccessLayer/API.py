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
        all_queries = []
        target_bounds = []

        # Get all the channel info
        meta_info = self._get_group_dict('')
        # The path and the  output format
        path = meta_info[info.PATH.NAME]
        out_format = self._get_list_query(in_info.FORMAT)
        # Get the name of the feature to load from db
        feat = self._get_list_query(feats)

        # All features that need id
        if feat in feats.ID_LIST:
            # get the id
            id_key = self._get_int_query(in_info.ID)
            # Return names based on id
            names = self._id_feature(feat, path, id_key)
        # All features that need bounds and id
        elif feat in feats.ID_BOX_LIST:
            # get the id
            id_key = self._get_int_query(in_info.ID)
            # get resolution from input
            res_xy = self.INPUT.RESOLUTION.XY
            resolution = self._get_int_query(res_xy)
            # get bounds from input
            for key in ['Z','Y','X','DEPTH','HEIGHT','WIDTH']:
                term = getattr(self.INPUT.POSITION, key)
                target_bounds.append(self._get_int_query(term))
            # scale the bounds from resolution
            scale = 2**resolution
            scales = np.tile([1 ,scale, scale], 2)
            bounds = np.uint32(target_bounds * scales)
            # Return names based on bounds
            names = self._id_box_feature(feat, path, id_key, bounds)
        # All features that need bounds
        elif feat in feats.BOX_LIST:
            # get resolution from input
            res_xy = self.INPUT.RESOLUTION.XY
            resolution = self._get_int_query(res_xy)
            # get bounds from input
            for key in ['Z','Y','X','DEPTH','HEIGHT','WIDTH']:
                term = getattr(self.INPUT.POSITION, key)
                target_bounds.append(self._get_int_query(term))
            # scale the bounds from resolution
            scale = 2**resolution
            scales = np.tile([1 ,scale, scale], 2)
            bounds = np.uint32(target_bounds * scales)
            # Return names based on bounds
            names = self._box_feature(feat, path, bounds)
        # All features needing no parameters
        else:
            names = self._static_feature(feat, path)

        # Return an infoquery
        return InfoQuery(**{
            methods.NAME: methods.FEAT.NAME,
            in_info.FORMAT.NAME: out_format,
            info.QUERY.NAME: all_queries,
            info.NAMES.NAME: names,
            info.PATH.NAME: path,
            feats.NAME: feat
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

        # Shorthand database name, table, key
        db, db_table, db_key = self._db_feature(feat)

        # Do not have
        if not db_table:
            return ['Voxel List not Supported']

        # Just check record of an ID
        if feat in feats.BOOL_LIST:
            if feat == k_tables.LIST[0]:
                return db.is_neuron(db_table, path, id_key)
            else:
                return db.is_synapse(db_table, path, id_key)

        # If the request gets a keypoint
        if feat in feats.POINT_LIST:
            # Get the resolution parameter
            res_xy = self.INPUT.RESOLUTION.XY
            resolution = self._get_int_query(res_xy)
            scales = 2**resolution
            # Load from either table
            if feat == k_tables.LIST[0]:
                return db.neuron_keypoint(db_table, path, id_key, scales)
            else:
                return db.synapse_keypoint(db_table, path, id_key, scales)

        # If the request asks for all links
        if feat == feats.SYNAPSE_LINKS.NAME:
            return db.synapse_parent(db_table, path, id_key)

        # Not yet supported
        return [db_table]

    def _id_box_feature(self, feat, path, id_key, bounds):
        """ Loads a feature list that needs a bounding box

        Calls :meth:`_db_feature` to access database

        Arguments
        -----------
        feat : str
            The name of the feature request
        path : str
            The path to the corresponding image data
        id_key : int
            The key value for a :class:`Database` table
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

        # Shorthand database name, table, key
        db, db_table, db_key = self._db_feature(feat)
        # Do not know
        if not db_table:
            return ['Feature not understood']

        # Get start and end of bounds
        start = np.uint32(bounds[:3])
        stop = start + bounds[3:]

        # Find all synapses where neuron is parent
        if feat == feats.NEURON_CHILDREN.NAME:
            # return pre and post results
            return db.neuron_children(db_table, path, id_key, start, stop)

        # Not yet supported
        return [db_table]

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

        # Shorthand database name, table, key
        db, db_table, db_key = self._db_feature(feat)
        # Do not know
        if not db_table:
            return ['Feature not understood']

        # Get start and end of bounds
        start = np.uint32(bounds[:3])
        stop = start + bounds[3:]

        # if request for labels in bounds
        if feat in feats.LABEL_LIST:
            # Find the center points within the bounds
            return db.synapse_ids(db_table, path, start, stop)

        # Not yet supported
        return [db_table]

    def _static_feature(self, feat, path):
        """ Loads a feature list that needs no parameters

        Calls :meth:`_db_feature` to access database

        Arguments
        -----------
        feat : str
            The name of the feature request
        path : str
            The path to the corresponding image data

        Returns
        --------
        list or dict
            The feature used to make an :class:`InfoQuery`
        """

        # Get input keyword arguments
        feats = self.INPUT.FEATURES
        # Get metadata for database
        k_tables = self.RUNTIME.DB.TABLE

        # Shorthand database name, table, key
        db, db_table, db_key = self._db_feature(feat)
        # Do not know
        if not db_table:
            return ['Feature not understood']

        # Return all keys in the table
        return db.all_neurons(db_table, path)

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
            Created with the :meth:`sub_data` for the full request
        """
        k_pos = self.INPUT.POSITION
        positions = map(k_pos.get, k_pos.LIST)
        # get integer bounds from POSITION LIST
        bounds = map(self._get_int_query, positions)

        # Create the data query for the full bounds
        return self.sub_data(_method, bounds)


    def sub_data(self, _method, bounds):
        """ Make :class:`DataQuery` for any subregion or request

        Arguments
        ----------
        _method: str
            The name of the method requesting image information
        bounds: numpy.ndarray
            The 6x1 array of z,y,x,depth,width,height values for \
the bounds requested for a data query

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
        terms = {
            path_key: meta_dict[path_key],
            self.INPUT.METHODS.NAME: _method
        }

        # get terms from IMAGE
        for key in ['VIEW','FORMAT']:
            term = getattr(self.INPUT.IMAGE, key)
            terms[term.NAME] = self._get_list_query(term)

        # get integers from bounds
        for order in range(6):
            key = self.INPUT.POSITION.LIST[order]
            terms[key] = bounds[order]

        # get integers from RESOLUTION
        term = self.INPUT.RESOLUTION.XY
        terms[term.NAME] = self._get_int_query(term)

        return DataQuery(**terms)

    ####
    # Handles Logs and Exceptions
    ####

    def _try_typecast_int(self, name, result):
        """ Try to convert a query result to an integer

        Arguments
        -----------
        name: str
            The name of the ``result`` property
        result: anything
            The value to try to convert to ``int``

        Returns
        ---------
        numpy.uint32
            If the ``result`` can convert to an integer
        """
        try:
            return int(result)
        except (TypeError, ValueError):
            msg = "The {0} {1} is not an integer."
            msg = msg.format(name, result)
            raise URLError([msg, 400])

    def _match_list(self, name, result, whitelist):
        """ Check if the query result is in a whitelist

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
        # Check if the result is in the list
        if result in whitelist:
            return result

        # Create the error message
        msg = "The {0} {1} is not in {2}."
        msg = msg.format(name, result, whitelist)
        raise URLError([msg, 400])

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
