from CoreLayer import UtilityLayer
from CoreLayer import DatabaseLayer
from Webserver import Webserver
import sys, argparse
import logging

class Butterfly():
    '''
    Butterfly 2.0
    EM Data server
    2017 VCG + Lichtman Lab
    '''
    log_info = {
        'filename': 'bfly.log',
        'level': logging.INFO
    }
    # Constants
    PORT = UtilityLayer.PORT
    DB_TYPE = UtilityLayer.DB_TYPE
    DB_PATH = UtilityLayer.DB_PATH
    BFLY_CONFIG = UtilityLayer.BFLY_CONFIG

    def __init__(self,_argv):

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
        # Get the correct database class
        db_class = getattr(DatabaseLayer, self.DB_TYPE)
        # Create the database with RUNTIME constants
        db = db_class(self.DB_PATH, self.RUNTIME)
        # Load database paths, tables, and entries
        return db.load_config(self.BFLY_CONFIG)

    def parse_argv(self, argv):
        sys.argv = argv

        helps = {
            'bfly': 'Host a butterfly server!',
            'folder': 'relative, absolute, or user path/of/all/experiments',
            'save': 'path of output yaml file indexing experiments',
            'port': 'port >1024 for hosting this server'
        }
        parser = argparse.ArgumentParser(description=helps['bfly'])
        parser.add_argument('port', **{
            'type': int,
            'nargs': '?',
            'default': self.PORT,
            'help': helps['port']
        })
        parser.add_argument('-e','--exp', metavar='exp', help=helps['folder'])
        parser.add_argument('-o','--out', metavar='out', help=helps['save'])
        return vars(parser.parse_args())

def main(args=None):
    Butterfly(sys.argv)

if __name__ == "__main__":
    main()
