import butterfly
import sys, argparse
from Test_Webserver import Test_Webserver

class Test():
    '''
    Butterfly 2.0
    EM Data server
    2017 VCG + Lichtman Lab
    '''
    units = {
        'Webserver': Test_Webserver
    }
    def __init__(self,_argv):

        args = self.parseArgv(_argv[:2])
        self._unit = args['unit']
        self._argv = _argv[1:]

    def start(self):
        unit = self._unit
        argv = self._argv
        if unit in self.units:
            return self.units[unit](argv)
        return 'Invalid Unit'

    def parseArgv(self, argv):
        sys.argv = argv

        help = {
            'test': 'Test a given unit in butterfly!',
            'unit':  ', '.join(self.units.keys())
        }

        parser = argparse.ArgumentParser(description=help['test'])
        parser.add_argument('unit', nargs='?', default='Webserver', help=help['unit'])
        return vars(parser.parse_args())

def main(*_args, **_flags):
    return Test(butterfly.toArgv(*_args, **_flags))

if __name__ == "__main__":
    print Test(sys.argv).start()
