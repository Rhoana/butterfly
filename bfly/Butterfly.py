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
    """

    #: Path to log at log priority level
    log_info = {
        'filename': UtilityLayer.LOG_PATH,
        'level': logging.INFO
    }
    #: Port for :class:`Webserver`
    PORT = UtilityLayer.PORT
    #: Class of :mod:`DatabaseLayer`
    DB_TYPE = UtilityLayer.DB_TYPE
    #: Relative path to .db file
    DB_PATH = UtilityLayer.DB_PATH
    # Loaded from the rh-config
    BFLY_CONFIG = UtilityLayer.BFLY_CONFIG

    def __init__(self, _argv):

        # keyword arguments
        self.INPUT = UtilityLayer.INPUT()
        self.OUTPUT = UtilityLayer.OUTPUT()
        self.RUNTIME = UtilityLayer.RUNTIME()

        # Get the port
        args = self.parse_argv(_argv)
        port = args['port']

        # Start to write to log files
        logging.basicConfig(**self.log_info)

        # Populate the database
        db = self.update_db()

        # Start a webserver on given port
        server = Webserver(db).start(port)
        server.start()

    # Update the database from the config file
    def update_db(self):
        """ Starts :mod:`DatabaseLayer`. :data:`DB_TYPE`.

        Loads the database with paths from :data:`BFLY_CONFIG`.
        """
        # Get the correct database class
        db_class = getattr(DatabaseLayer, self.DB_TYPE)
        # Create the database with RUNTIME constants
        db = db_class(self.DB_PATH, self.RUNTIME)
        # Load database paths, tables, and entries
        return db.load_config(self.BFLY_CONFIG)

    @staticmethod
    def get_parser():
        """ Makes an argv parser for Butterfly

        Returns
        ----------
        argparse.ArgumentParser
            Can turn argv lists into args and keywords
        """
        helps = {
            'bfly': 'Host a butterfly server!',
            'out': 'path to output yaml config file',
            'exp': 'path/of/all/data or path/to/config',
            'port': 'port >1024 for hosting this server',
        }
        sys.argv[0] = 'bfly'
        _port = UtilityLayer.PORT
        parser = argparse.ArgumentParser(description=helps['bfly'])
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
        sys.argv = argv
        # Get the parser
        parser = self.get_parser()
        # Actually parse the arguments 
        return vars(parser.parse_args())

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

    Butterfly(UtilityLayer.to_argv(*args, **flags))

if __name__ == "__main__":
    Butterfly(sys.argv)
