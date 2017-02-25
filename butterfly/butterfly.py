from Webserver import Webserver
from toArgv import toArgv
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

        args = self.parseArgv(_argv)
        port = args['port']

        logging.basicConfig(**self.log_info)
        Webserver().start(port)

    def parseArgv(self, argv):
        sys.argv = argv

        help = {
            'bfly': 'Host a butterfly server!',
            'folder': 'relative, absolute, or user path/of/all/experiments',
            'save': 'path of output yaml file indexing experiments',
            'port': 'port >1024 for hosting this server'
        }

        parser = argparse.ArgumentParser(description=help['bfly'])
        parser.add_argument('port', type=int, nargs='?', default=2001, help=help['port'])
        parser.add_argument('-e','--exp', metavar='exp', help= help['folder'])
        parser.add_argument('-o','--out', metavar='out', help= help['save'])
        return vars(parser.parse_args())

def main(*_args, **_flags):
    return Butterfly(toArgv(*_args, **_flags))

if __name__ == "__main__":
    Butterfly(sys.argv)
