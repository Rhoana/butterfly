import bfly
import unittest as ut
import datetime
import logging
import sys

class TestWebserver(ut.TestCase):
    '''
    Butterfly 2.0
    Test the EM Data server
    2017 VCG + Lichtman Lab
    '''
    PORT = 2017
    DB_PATH = ':mem:'
    DB_TYPE = 'Unqlite'
    RUNTIME = bfly.UtilityLayer.RUNTIME()
    # Log to the command line
    log_info = {
        'stream': sys.stdout,
        'level': logging.INFO
    }

    @classmethod
    def test_web(cls):

        # Log to command line
        logging.basicConfig(**cls.log_info)

        # Make a dummy database
        db_class = getattr(bfly.DatabaseLayer, cls.DB_TYPE)
        db = db_class(cls.DB_PATH, cls.RUNTIME)

        # Make a dummy webserver
        web = bfly.Webserver(db)
        server = web.start(cls.PORT)

        # Stop the webserver after 1 second
        one_sec = datetime.timedelta(seconds=1)
        server.add_timeout(one_sec, web.stop)

        # Start the webserver right now
        server.start()

if __name__ == '__main__':
    ut.main()
