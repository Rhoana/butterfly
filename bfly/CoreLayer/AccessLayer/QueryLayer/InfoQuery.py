from Query import Query
import json, yaml

class InfoQuery(Query):
    """ Describe ``INPUT.METHODS.INFO_LIST`` requests

    Arguments
    -----------
    args: list
        unused
    keywords: dict
        * `OUTPUT.INFO.NAMES` (list) --
            all answers to group and feature queries
        * `OUTPUT.INFO.PATH` (str) --
            the path to the given :class:`Datasource`
        * `OUTPUT.INFO.SIZE` (numpy.ndarray) --
            3x1 for full volume shape
        * `OUTPUT.INFO.CHANNEL` (str) --
            The name of the most specific image group
        * `OUTPUT.INFO.FORMAT` (str) --
            The requested format for HTTP output

    Attributes
    ------------
    _write: list
        All write functions for output formats
    """

    #: Options for all :data:`_write`
    _form = [
       { 'indent': 4 },
       { 'default_flow_style': False }
    ]
    # All writers for output formats
    _write = [json.dumps, yaml.dump]

    def __init__(self,*args,**keywords):

        Query.__init__(self, **keywords)

        for key in ['NAMES','PATH','SIZE','CHANNEL']:
            self.set_key(self.OUTPUT.INFO,key)

        self.set_key(self.INPUT.INFO,'FORMAT')

    @property
    def key(self):
        """ return the key for the database

        Returns
        -------
        str
            the path value from ``OUTPUT.INFO``
        """
        return self.OUTPUT.INFO.PATH.VALUE

    @property
    def get_format(self):
        """ get the index of the output format

        Returns
        -------
        int
            index for :data:`_form` or :data:`_write`
        """
        fmt_val = self.INPUT.INFO.FORMAT.VALUE
        return self.INPUT.INFO.FORMAT.LIST.index(fmt_val)

    @property
    def result(self):
        """ get the answer to the info query

        Returns
        -------
        dict
            For the method ``INPUT.METHODS.META.NAME``:

            * ``OUTPUT.INFO.PATH.NAME`` --
                (str) ``OUTPUT.INFO.PATH.VALUE``
            * ``OUTPUT.INFO.TYPE.NAME`` --
                (str) ``OUTPUT.INFO.TYPE.VALUE``
            * ``OUTPUT.INFO.SIZE.NAME`` --
                (dict) ``OUTPUT.INFO.SIZE.VALUE``
            * ``OUTPUT.INFO.CHANNEL.NAME`` --
                (str) ``OUTPUT.INFO.CHANNEL.VALUE``
        list
            For all methods ``INPUT.METHODS.GROUP_LIST``:
            For the method ``INPUT.METHODS.FEATURE.NAME``:

            * all (str) in ``OUTPUT.INFO.NAMES.VALUE``
        """

        info_out = self.OUTPUT.INFO
        methods = self.INPUT.METHODS
        if methods.VALUE in methods.GROUP_LIST:
            return info_out.NAMES.VALUE
        if methods.VALUE == methods.META.NAME:
            return {
                info_out.PATH.NAME: info_out.PATH.VALUE,
                info_out.TYPE.NAME: info_out.TYPE.VALUE,
                info_out.SIZE.NAME: info_out.SIZE.VALUE,
                info_out.CHANNEL.NAME: info_out.CHANNEL.VALUE
            }
        return info_out.NAMES.VALUE

    @property
    def dump(self):
        """ format :meth:`result` with :data:`write`

        Returns
        --------
        str
            The :meth:`result` formatted as a string
        """
        out = self.get_format
        raw_output = self.result
        return self._write[out](raw_output,**self._form[out])

