from Webserver import Webserver
from toArgv import toArgv
from Settings import *
import DatabaseLayer
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
    def __init__(self,_argv):

        # keyword arguments
        self.INPUT = INPUT()
        self.RUNTIME = RUNTIME()
        self.OUTPUT = OUTPUT()

        # Get the port
        args = self.parseArgv(_argv)
        port = args['port']

        # Start to write to log files
        logging.basicConfig(**self.log_info)

        # Populate the database
        db = self.updateDB()

        # Start a webserver on given port
        Webserver(db).start(port)

    # Update the database from the config file
    def updateDB(self):
        # Create or open the database
        db_class = getattr(DatabaseLayer,DB_TYPE)
        db = db_class(DB_PATH)
        # Get keywords for the BFLY_CONFIG
        k_list = self.INPUT.METHODS.GROUP_LIST
        k_path = self.OUTPUT.INFO.PATH.NAME
        '''
        Make a dictionary mapping channel paths to dataset paths
        '''
        pather = lambda l: l.get(k_path,'')
        lister = lambda l,n: l.get(k_list[n],[])
        mapper  = lambda l,p: {c:p for c in map(pather,l)}
        join = lambda l,p,a: dict(mapper(l,p),**a) if p else a
        get_L2 = lambda a,l: join(lister(l,3), pather(l), a)
        get_L1 = lambda a,l: reduce(get_L2, lister(l,2), a)
        get_L0 = lambda a,l: reduce(get_L1, lister(l,1), a)
        all_paths = reduce(get_L0, lister(BFLY_CONFIG,0), {})

        # Fill the database with content
        return self.completeDB(db, all_paths)

    # Add all colections and content to the database
    def completeDB(self, db, all_paths):
        # Get keywords for the database
        k_path = self.RUNTIME.DB.TABLE.PATH.NAME

        # Add paths to database
        db.add_paths(all_paths)
        # Add all needed tables to the database
        db.add_tables(set(all_paths.values()))

        # Begin adding neurons and synapses to database

        return db

    def parseArgv(self, argv):
        sys.argv = argv

        help = {
            'bfly': 'Host a butterfly server!',
            'folder': 'relative, absolute, or user path/of/all/experiments',
            'save': 'path of output yaml file indexing experiments',
            'port': 'port >1024 for hosting this server'
        }

        parser = argparse.ArgumentParser(description=help['bfly'])
        parser.add_argument('port', type=int, nargs='?', default=PORT, help=help['port'])
        parser.add_argument('-e','--exp', metavar='exp', help= help['folder'])
        parser.add_argument('-o','--out', metavar='out', help= help['save'])
        return vars(parser.parse_args())

def main(*_args, **_flags):
    return Butterfly(toArgv(*_args, **_flags))

if __name__ == "__main__":
    Butterfly(sys.argv)
