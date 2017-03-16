from CoreLayer import Utility
from CoreLayer import Database
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
    def __init__(self,_argv):

        # keyword arguments
        self.INPUT = Utility.INPUT()
        self.OUTPUT = Utility.OUTPUT()
        self.RUNTIME = Utility.RUNTIME()

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
        db_class = getattr(Database, Utility.DB_TYPE)
        # Create the database with RUNTIME constants
        self._db = db_class(Utility.DB_PATH, self.RUNTIME)
        # Get keywords for the BFLY_CONFIG
        k_list = self.INPUT.METHODS.GROUP_LIST
        k_path = self.OUTPUT.INFO.PATH.NAME
        '''
        Make a dictionary mapping channel paths to dataset paths
        '''
        layer0 = Utility.BFLY_CONFIG
        pather = lambda l: l.get(k_path,'')
        lister = lambda l,n: l.get(k_list[n],[])
        mapper  = lambda l,p: {c:p for c in map(pather,l)}
        join = lambda l,p,a: dict(mapper(l,p),**a) if p else a
        get_layer2 = lambda a,l: join(lister(l,3), pather(l), a)
        get_layer1 = lambda a,l: reduce(get_layer2, lister(l,2), a)
        get_layer0 = lambda a,l: reduce(get_layer1, lister(l,1), a)
        all_paths = reduce(get_layer0, lister(layer0,0), {})

        # Fill the database with content
        return self._db.add_paths(all_paths)

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
            'default': Utility.PORT,
            'help': helps['port']
        })
        parser.add_argument('-e','--exp', metavar='exp', help=helps['folder'])
        parser.add_argument('-o','--out', metavar='out', help=helps['save'])
        return vars(parser.parse_args())

def main(args=None):
    Butterfly(sys.argv)

if __name__ == "__main__":
    main()
