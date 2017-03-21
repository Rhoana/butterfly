from CoreLayer import UtilityLayer
from CoreLayer import DatabaseLayer
from Webserver import Webserver
import sys, argparse
import logging

class Butterfly():
    """Starts :class:`bfly.Webserver` and runs :meth:`update_db`.

    :param list _argv:
        passed through :meth:`parse_argv`
    """
    log_info = {
        'filename': UtilityLayer.LOG_PATH,
        'level': logging.INFO
    }
    PORT = UtilityLayer.PORT
    """ Port for :class:`Webserver` """
    DB_TYPE = UtilityLayer.DB_TYPE
    """ Class of :mod:`DatabaseLayer` """
    DB_PATH = UtilityLayer.DB_PATH
    """ Relative path to .db file """
    BFLY_CONFIG = UtilityLayer.BFLY_CONFIG
    # Loaded from the rh-config

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
        """:return argparse.ArgumentParser
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

        :param list argv:
            parsed as sys.argv by argparse
        :return dict:
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

    :param list args:
        * [0] (int) -- port for :class:`bfly.Webserver`
    :param dict flags:
        * exp (str) -- path to config or folder of data
        * out (str) -- path to save config from folder
    """

    Butterfly(UtilityLayer.to_argv(*args, **flags))

if __name__ == "__main__":
    Butterfly(sys.argv)
