from CoreLayer import UtilityLayer
from CoreLayer import DatabaseLayer
from Webserver import Webserver
import sys, argparse
import logging

class Butterfly():
    """Starts :class:`bfly.Webserver` and runs :meth:`update_db`.

    Args
    -------
    _argv : list
        passed through :meth:`parse_argv`

    Attributes
    -----------
        _bfly_config : dict
            all data from rh-config
        _runtime : :class:`UtilityLayer.RUNTIME`
            has settings for :mod:`CoreLayer`

    """

    #: path to log and the log priority level
    _log_info = {
        'filename': UtilityLayer.LOG_PATH,
        'level': logging.INFO
    }
    #: class of :mod:`DatabaseLayer`
    _db_type = UtilityLayer.DB_TYPE
    #: relative path to .db file
    _db_path = UtilityLayer.DB_PATH

    # loaded from the rh-config
    _bfly_config = UtilityLayer.BFLY_CONFIG
    # keyword arguments for :mod:`CoreLayer`
    _runtime = UtilityLayer.RUNTIME()

    def __init__(self, _argv):

        # Get the port
        args = self.parse_argv(_argv)
        port = args['port']

        # Start to write to log files
        logging.basicConfig(**self._log_info)

        # Populate the database
        db = self.update_db()

        # Start a webserver on given port
        server = Webserver(db).start(port)
        server.start()

    # Update the database from the config file
    def update_db(self):
        """ Starts :mod:`DatabaseLayer`. :data:`_db_type`.

        Loads the database with paths from :data:`_bfly_config`.
        """

        # Get the correct database class
        db_class = getattr(DatabaseLayer, self._db_type)
        # Create the database with runtime constants
        db = db_class(self._db_path, self._runtime)
        # Load database paths, tables, and entries
        return db.load_config(self._bfly_config)

    @staticmethod
    def get_parser():
        """ Makes an argv parser for ``Butterfly``.

        Returns
        ----------
        argparse.ArgumentParser
            map from argv lists to args and keywords
        """

        helps = {
            'bfly': 'Host a butterfly server!',
            'out': 'path to output yaml config file',
            'exp': 'path/of/all/data or path/to/config',
            'port': 'port >1024 for hosting this server',
        }
        _port = UtilityLayer.PORT
        parser = argparse.ArgumentParser(prog= 'bfly',
                            description= helps['bfly'])
        parser.add_argument('port', type= int, nargs= '?',
                            default= _port, help= helps['port'])
        parser.add_argument('-e','--exp', help= helps['exp'])
        parser.add_argument('-o','--out', help= helps['out'])
        # return the parser
        return parser

    def parse_argv(self, argv):
        """Converts argv list to dictionary with defaults.

        Args
        -------
        argv : list
            parsed as sys.argv by argparse
        Returns
        ---------
        dict
            * port (int) -- for :class:`bfly.Webserver`
            * exp (str) -- path to config or folder of data
            * out (str) -- path to save config from folder
        """

        # Get the parser
        parser = self.get_parser()
        # Actually parse the arguments 
        parsed = parser.parse_args(argv[1:])
        return vars(parsed)

def main(*args, **flags):
    """Starts a :class:`Butterfly` with arguments.

    Args
    ------
    args : list
        * [0] (int) -- port for :class:`bfly.Webserver`
    flags: dict
        * exp (str) -- path to config or folder of data
        * out (str) -- path to save config from folder
    Returns
    --------
    Butterfly
        This instance handles everything internally
    """
    argv = UtilityLayer.to_argv(*args, **flags)
    Butterfly(argv)

if __name__ == "__main__":
    Butterfly(sys.argv)
