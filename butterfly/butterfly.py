from Webserver import Webserver
import sys, argparse
import logging

def start(_argv):
    '''
    Butterfly 2.0
    EM Data server
    2017 VCG + Lichtman Lab
    '''
    begin ='''
Started Butterfly on port {port}
    '''

    args = parseArgv(_argv)
    port = args['port']

    logging.basicConfig(filename='bfly.log', level=logging.INFO)
    begin_log = begin.replace('{port}',str(port))
    logging.info(begin_log)

    # discovery for image data
        ## Make an rh-config

    ## connect to database

    # discovery for database
        ## From BFLY_CONFIG we look only into datasets.path for json files

        ## check if new data is in file system
        ## for this we need to check in the database for the dataset.path as keys

    


    server = Webserver(port)
    return 0

def parseArgv(argv):
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

# Allow Common Command Line / Module Interface

def toArgv(*args, **flags):
    keyvals = flags.items()
    all_tokens = range(2*len(keyvals))
    endash = lambda fkey: '-'+fkey if len(fkey) == 1 else '--'+fkey
    enflag = lambda kv,fl: str(kv[fl]) if fl else endash(str(kv[fl]))
    kargv = [enflag(keyvals[i//2],i%2) for i in all_tokens]
    return ['main'] + list(map(str,args)) + kargv

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)
