import os
import logging
from butterfly import Webserver
import sys, argparse

class Test_Webserver():
    '''
    Butterfly 2.0
    EM Data server
    2017 VCG + Lichtman Lab
    '''
    log_info = {
        'filename': os.path.join('logs','Webserver.log'),
        'level': logging.INFO
    }
    def __init__(self,_argv):

        args = self.parseArgv(_argv)
        port = args['port']
        logging.basicConfig(**self.log_info)
        self._server = Webserver().start(port)
        return self._bfly.start()

    def parseArgv(self, argv):
        sys.argv = argv

        help = {
            'test': 'Test Webserver unit in butterfly!',
            'port': 'port >1024 for hosting this server'
        }

        parser = argparse.ArgumentParser(description=help['test'])
        parser.add_argument('port', nargs='?', default=2001, help=help['port'])
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
    return Test_Webserver(toArgv(*_args, **_flags))

if __name__ == "__main__":
    Test_Webserver(sys.argv)
