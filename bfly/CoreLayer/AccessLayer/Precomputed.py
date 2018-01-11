from RequestHandler import RequestHandler
from QueryLayer import InfoQuery
from QueryLayer import DataQuery
from urllib2 import URLError
import numpy as np
import os

def get_name(g):
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
    k_name = RequestHandler.INPUT.GROUP.NAME
    return g.get(k_name, '')

def match_list(name, result, whitelist):
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

def get_config(_config, _keywords, _channel=False):
    """ get the config dictionary for the requested method

    Arguments
    ----------
    _config: dict
        Root configuration of experiments
    _keywords: dict
        All URL parameters
    _channel: bool
        Get Specific Channel information if true

    Returns
    --------
    dict
        The requested sub-dictionary from :data:`BFLY_CONFIG`
    """
    configured = dict(_config)
    group_keys = list(RequestHandler.INPUT.METHODS.GROUP_LIST)

    # Get all the input token groups
    tokens = _keywords.get('token','').split('::')
    tokens.append(_keywords.get('channel',''))

    # Ignore channel information
    if not _channel:
        group_keys.pop(-1)

    # Make dictionary of all input token groups
    token_groups = dict(zip(group_keys, tokens))

    # validate each group in token
    for g_key in group_keys:
        # Get all valid group names
        valid_groups = configured.get(g_key, [])
        valid_names = map(get_name, valid_groups)
        # Check group against all valid group names
        group_name = token_groups.get(g_key, '')
        match_list(g_key, group_name, valid_names)
        # Check next group name in the token
        group_index = valid_names.index(group_name) 
        configured = valid_groups[group_index]

    # Return info for full token
    return configured

############
# Actual Precomputed class
####
class Precomputed(RequestHandler):
    """ Responds to :data:`bfly.Webserver._webapp` /nd endpoint

    Attributes
    -----------
    inherits: :class:`RequestHandler`


    :h:`Methods`

    """
    # http://docs.neurodata.io/ndstore/api/info_api.html
    INFO_API = [
        'token',
        'channel',
        'action'
    ]

    DATA_API = [
        'token',
        'channel',
        'resolution',
        'xmin-xmax',
        'ymin-ymax',
        'zmin-zmax',
    ]

    def parse(self, request):
        """ Extract details from any of the methods
        Overrides :meth:`Database.parse`

        Arguments
        ----------
        request: str
            The full request

        Returns
        ---------
        :class:`QueryLayer.Query`
            contains standard details for each request
        """
        super(Precomputed, self).parse(request)
        # Store the request
        args = request.split('/')

        # Interpret first arguments
        keywords = dict(zip(self.INFO_API, args)) 

        # Get the meshes
        if keywords['action'] == 'mesh':
            mesh_args = args[:2] + args[3:]
            mesh_args = ['static','mesh'] + mesh_args
            return str('/'.join(mesh_args))

        # Handle the info API
        if keywords['action'] == 'info':
            return self.get_info(keywords)

        # Also split bounds by underscore
        bounds = args.pop()
        args += bounds.split('_')

        # Handle volume API
        keywords = dict(zip(self.DATA_API, args))
        return self.get_vol(keywords)

    #####
    #Loads precomputed info
    #####
    def get_info(self, _keywords):
        """ Loads :class:`InfoQuery` for ``INPUT.METHODS.META``

        Returns
        --------
        :class:`InfoQuery`
            made with info from ``get_config``
        """
        # Parse all the group terms
        chan_dict = get_config(self.BFLY_CONFIG, _keywords, True)

        # Get keys for interface
        chan_key = self.OUTPUT.INFO.CHANNEL.NAME
        format_key = self.INPUT.INFO.FORMAT.NAME
        k_pre_info = self.INPUT.METHODS.PRE.NAME
        path_key = self.OUTPUT.INFO.PATH.NAME
        method_key = self.INPUT.METHODS.NAME

        return InfoQuery(**{
            chan_key: get_name(chan_dict),
            path_key: chan_dict[path_key],
            method_key: k_pre_info,
            format_key: 'json',
        })

    #####
    #Loads data from tiles for image methods
    #####

    def get_vol(self, _keywords):
        """ Make :class:`DataQuery` for an image at request path

        Arguments
        ----------
        _keywords: dict
            All URL parameters

        Returns
        --------
        :class:`DataQuery`
            Created with the :meth:`sub_data` for the full request
        """
        # Get the input terms
        xmin, xmax = self._get_ints(_keywords, 'xmin-xmax', '0-512') 
        ymin, ymax = self._get_ints(_keywords, 'ymin-ymax', '0-512') 
        zmin, zmax = self._get_ints(_keywords, 'zmin-zmax', '0-1') 
        resolution = self._get_int(_keywords, 'resolution', '0')

        # Get format
        img_fmt = 'raw'
 
        # Compute standard bounds
        bounds = [
            zmin,
            ymin,
            xmin,
            zmax - zmin,
            ymax - ymin,
            xmax - xmin,
        ]

        # Create the data query for the full bounds
        return self.sub_data(_keywords, bounds, resolution, img_fmt)


    def sub_data(self, _keywords, bounds, resolution, img_fmt='tif'):
        """ Make :class:`DataQuery` for any subregion or request

        Arguments
        ----------
        _keywords: dict
            All URL parameters
        bounds: numpy.ndarray
            The 6x1 array of z,y,x,depth,width,height values for \
the bounds requested for a data query
        resolution: int
            the number of halvings along the X and Y axes

        Returns
        --------
        :class:`DataQuery`
        """
        # Parse all the group terms
        meta_dict = get_config(self.BFLY_CONFIG, _keywords, True)

        # Get keys for API interfaces
        resolution_key = self.INPUT.RESOLUTION.XY.NAME
        format_key = self.INPUT.IMAGE.FORMAT.NAME
        view_key = self.INPUT.IMAGE.VIEW.NAME
        method_key = self.INPUT.METHODS.NAME
        # Get keys from file interfaces
        offset_key = self.INPUT.IMAGE.OFFSET.NAME
        path_key = self.OUTPUT.INFO.PATH.NAME

        # Begin building needed keywords
        terms = {
            offset_key: meta_dict.get(offset_key, [0,0,0]),
            path_key: meta_dict.get(path_key, ''),
            resolution_key: resolution,
            format_key: img_fmt,
            view_key: 'grayscale',
            method_key: 'data',
        }

        # get integers from bounds
        for order in range(6):
            key = self.INPUT.POSITION.LIST[order]
            terms[key] = bounds[order]

        return DataQuery(**terms)

    ####
    # Handles Logs and Exceptions
    ####

    def _try_int(self, name, result):
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

    def _get_int(self, keywords, name, value=''):
        """ Call :meth:`_try_int` on the keywords

        Arguments
        ----------
        keywords: dict
            All URL parameters
        name: str
            the name of the property
        value: anything
            the default property value

        Returns
        ---------
        int
            If the ``result`` can be converted to an integer
        """
        result = keywords.get(name, value)
        return self._try_int(name, result)

    def _get_ints(self, keywords, name, value=''):
        """ Call :meth:`_try_ints` on the keywords

        Arguments
        ----------
        keywords: dict
            All URL parameters
        name: str
            the name of the property
        value: anything
            the default property value

        Returns
        ---------
        [int]
            If the ``result`` can be converted to an integer list
        """
        result = keywords.get(name, value)
        def try_int(i):
            return self._try_int(name, i)
        # Try int on all results
        return map(try_int, result.split('-'))
