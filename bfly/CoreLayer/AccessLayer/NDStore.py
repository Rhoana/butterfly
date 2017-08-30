from RequestHandler import RequestHandler
from QueryLayer import InfoQuery
from QueryLayer import DataQuery
from urllib2 import URLError
import numpy as np

class NDStore(RequestHandler):
    """ Responds to :data:`bfly.Webserver._webapp` /nd endpoint

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

        super(NDStore, self).parse(request)

        a = request.split('/')
        print a
        # Always get data
        return self.get_data(command)

        return 'Unsupported Request Category'

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
