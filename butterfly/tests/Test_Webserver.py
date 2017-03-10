import butterfly
from unittest import TestCase

class Test_Webserver(TestCase):
    '''
    Butterfly 2.0
    Test the EM Data server
    2017 VCG + Lichtman Lab
    '''
    PORT = 2017

    def __init__(args=None):

        self._server = butterfly.Webserver()
        self._server.start(PORT)
