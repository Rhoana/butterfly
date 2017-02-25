import os
import logging
import butterfly
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
        self._server = butterfly.Webserver()
        self._server.start(port)

    def parseArgv(self, argv):
        sys.argv = argv

        help = {
            'test': 'Test Webserver unit in butterfly!',
            'port': 'port >1024 for hosting this server'
        }

        parser = argparse.ArgumentParser(description=help['test'])
        parser.add_argument('port', nargs='?', default=2001, help=help['port'])
        return vars(parser.parse_args())

def main(*_args, **_flags):
    return Test_Webserver(butterfly.toArgv(*_args, **_flags))

if __name__ == "__main__":
    Test_Webserver(sys.argv)
