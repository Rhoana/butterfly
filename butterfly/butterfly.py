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
        # Open data in the BFLY_CONFIG
        k_list = self.INPUT.METHODS.GROUP_LIST
        k_path = self.OUTPUT.INFO.PATH.NAME
        '''
        Make a dictionary with
            keys given by dataset path
            values as lists of channel paths
        '''
        get_path = lambda l: l.get(k_path,'')
        all_path = lambda l: map(get_path, l[k_list[3]])
        new_dict = lambda l,p: {p: all_path(l)} if p else {}
        join_dict = lambda a,l,p: dict(a, **new_dict(l, p))
        get_L2 = lambda a,l: join_dict(a, l, l.get(k_path,''))
        get_L1 = lambda a,l: reduce(get_L2, l[k_list[2]], a)
        get_L0 = lambda a,l: reduce(get_L1, l[k_list[1]], a)
        all_paths = reduce(get_L0, BFLY_CONFIG[k_list[0]], {})
        print all_paths
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
