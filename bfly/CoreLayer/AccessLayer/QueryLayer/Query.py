from mimetypes import types_map
from UtilityLayer import INPUT
from UtilityLayer import RUNTIME
from UtilityLayer import OUTPUT
from urllib2 import URLError
import logging as log
import numpy as np

class Query():
    """ Describe content of :mod:`AccessLayer` requests

    Arguments
    -----------
    args: list
        See :class:`TileQuery` for use of positional arguments
    keywords: dict
        Each derived class may use any keyword arguments given \
keys each match a `NAME` of a :class:`NamedStruct`in \
:class:`INPUT`, :class:`RUNTIME`, or :class:`OUTPUT`.

    Attributes
    ------------
        INPUT: :class:`INPUT`
        RUNTIME: :class:`RUNTIME`
        OUTPUT: :class:`OUTPUT`
        keywords: dict
            Taken from ``keywords`` argument
    """
    #: default mime type for HTTP response
    _basic_mime = 'text/plain'

    def __init__(self,*args,**keywords):
        self.INPUT = INPUT()
        self.RUNTIME = RUNTIME()
        self.OUTPUT = OUTPUT()

        # Get method and feature
        method = keywords.get(self.INPUT.METHODS.NAME,'')
        feature = keywords.get(self.INPUT.FEATURES.NAME,'')
        # Set method and feature
        self.INPUT.METHODS.VALUE = method
        self.INPUT.FEATURES.VALUE = feature

        # Get and set the linked list of queries
        queries = keywords.get(self.OUTPUT.INFO.QUERY.NAME,'')
        self.OUTPUT.INFO.QUERY.VALUE = queries

        # Permanently store the keywords
        self.keywords = {}
        self.update_keys(keywords)

    def update_keys(self, keywords):
        """ Update stored keywords

        Arguments
        ----------
        keywords: dict
            Updates stored keywords
        """
        self.keywords.update(keywords)

    def set_key(self, struct, key, empty=''):
        """ Copy the key from keywords to the structure

        Arguments
        ----------
        struct: :class:`NamelessStruct`
            Where to store a value from :data:`keywords`
        key: str
            The key to transfer from :data:`keywords`
        empty: anything
            The value if :data:`keywords` has no ``key``\
and the ``key`` has no default in the struct
        """
        # Get field to be set
        field = struct.get(key, {})
        # Get default value from struct
        default = field.get('VALUE', empty)
        # Get value from input keywords if exists
        val = self.keywords.get(field.NAME, default)
        # Set keyword value to field
        setattr(field, 'VALUE', val)

    @property
    def is_data(self):
        """ Checks whether the method requests images

        Returns
        -------
        bool
        """
        image_methods = self.INPUT.METHODS.IMAGE_LIST
        return self.INPUT.METHODS.VALUE in image_methods

    @property
    def is_group(self):
        """ Checks whether the method requests groups

        Returns
        -------
        bool
        """
        group_methods = self.INPUT.METHODS.GROUP_LIST
        return self.INPUT.METHODS.VALUE in group_methods

    @property
    def is_dataset(self):
        """ Checks if requesting dataset info

        Returns
        -------
        bool
        """
        dataset_list = ['project_info']
        return self.INPUT.METHODS.VALUE in dataset_list

    @property
    def mime_type(self):
        """ Gets the mime type for the file_type

        The mime type is from :data:`INPUT.IMAGE` \
if :meth:`is_data`, or :data:`INPUT.INFO` \
otherwise.

        Returns
        --------
        str
            The mime type from ``mimetypes.types_map``
        """
        info_type = self.INPUT.INFO.FORMAT.VALUE
        image_type = self.INPUT.IMAGE.FORMAT.VALUE
        # Use image type for data and info type for info
        file_type = image_type if self.is_data else info_type
        # Get the right mime type or use default for this class
        _basic_mime = self._basic_mime.format(file_type)
        return types_map.get('.'+file_type, _basic_mime)

    def update_source(self, keywords):
        """ Set all attribute values to match keywords

        Arguments
        ----------
        keywords: dict
            * :class:`RUNTIME` ``.IMAGE.SOURCE.NAME``
                (str) -- The subclass of :class:`Datasource`
            * :class:`RUNTIME` ``.IMAGE.BLOCK.NAME``
                (numpy.ndarray) -- 3x1 for any given tile shape
            * :class:`OUTPUT` ``.INFO.TYPE.NAME``
                (str) -- numpy dtype of any given tile
            * :class:`OUTPUT` ``.INFO.SIZE.NAME``
                (numpy.ndarray) -- 3x1 for full volume shape

            Keyword arguments only for :class:`HDF5`

            * :class:`RUNTIME` ``.IMAGE.SOURCE.HDF5.OUTER.NAME``
                (str) -- The direct filename to an hdf5 file
            * :class:`RUNTIME` ``.IMAGE.SOURCE.HDF5.INNER.NAME``
                (str) -- The dataset in the file with image data
        """
        # take named keywords
        output = self.OUTPUT.INFO
        runtime = self.RUNTIME.IMAGE
        # Get the right kind of datasource and datatype
        source_val = keywords.get(runtime.SOURCE.NAME)
        type_val = keywords.get(output.TYPE.NAME)
        # Get the right blocksize
        block = keywords.get(runtime.BLOCK.NAME)
        # Unpack dimensions for full volume
        full_size = keywords.get(output.SIZE.NAME, [0,0,0])

        # Make sure the source and type are valid
        self.check_list(runtime.SOURCE.LIST, source_val, 'source')
        self.check_list(output.TYPE.LIST, type_val, 'type')
        # Make sure the size has a length of 3
        self.check_vector(full_size, 'volume', 3)
        # Make sure all blocks are valid
        for block_i in block:
            msg = 'bigger than {}'.format(block_i)
            # Make sure each blocksize has length 3
            self.check_vector(block_i, 'block', 3)
            # Make sure size is bigger than each blocksize
            if not np.all(np.uint32(block_i) <= full_size):
                msg = 'A {} block will not fit in a {} volume'
                msg = msg.format(block_i, full_size)
                raise URLError([msg, 503])

        # Set all the clean values
        output.TYPE.VALUE = type_val
        runtime.SOURCE.VALUE = source_val
        runtime.BLOCK.VALUE = np.uint32(block)

        # Set the output size
        output.SIZE.VALUE = {
            output.SIZE.Z.NAME: int(full_size[0]),
            output.SIZE.Y.NAME: int(full_size[1]),
            output.SIZE.X.NAME: int(full_size[2])
        }

        ##############
        # Optional keywords by source

        # HDF5
        h5_field = runtime.SOURCE.HDF5
        h5_field.VALUE = keywords.get(h5_field.NAME)

        # Mojo
        mojo_format = runtime.SOURCE.MOJO.FORMAT
        mojo_format.VALUE = keywords.get(mojo_format.NAME)

    def check_list(self, whitelist, value, term):
        """ Checks that a value is in a given list

        Arguments
        -----------
        whitelist: list-like
            The list of desired values
        value: anything
            The value should be in the ``whitelist``
        term: str
            The name of the attribute to test
        """
        if not value in whitelist:
            msg = 'The {} {} is not in {}'.format(term, value, whitelist)
            raise URLError([msg, 503])

    def check_vector(self, value, term='list', dims=3):
        """ Checks that a vector has three dimensions

        Arguments
        -----------
        term: str
            The name of the attribute to test
        value: list-like
            The value should be a list or array
        dims: int
            The desired number of dimensions
        """
        try:
            return int(value[0])
        except (TypeError, ValueError, IndexError):
            msg = 'The {} {} is not a vector'
            msg = msg.format(term, value)
            raise URLError([msg, 503])

        # Check length if length given
        if len(value) != dims:
            msg = 'The {} {} does not have {} dimensions'
            msg = msg.format(term, value, dims)
            raise URLError([msg, 503])
