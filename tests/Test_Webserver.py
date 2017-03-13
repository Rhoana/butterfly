from tornado.ioloop import IOLoop
import butterfly as bfly
import unittest as ut
import datetime
import logging
import sys

class Test_Webserver(ut.TestCase):
    '''
    Butterfly 2.0
    Test the EM Data server
    2017 VCG + Lichtman Lab
    '''
    PORT = 2017
    DB_PATH = ':mem:'
    DB_TYPE = 'Unqlite'
    RUNTIME = bfly.Utility.RUNTIME()
    # Log to the command line
    log_info = {
        'stream': sys.stdout,
        'level': logging.INFO
    }

    @classmethod
    def test_web(_test):

        # Log to command line
        logging.basicConfig(**_test.log_info)

        # Make a dummy database
        db_class = getattr(bfly.Database, _test.DB_TYPE)
        db = db_class(_test.DB_PATH, _test.RUNTIME)

        # Make a dummy webserver
        web = bfly.Webserver(db)
        server = web.start(_test.PORT)

        # Stop the webserver after 1 second
        one_sec = datetime.timedelta(seconds=1)
        server.add_timeout(one_sec, web.stop)

        # Start the webserver right now 
        server.start()

if __name__ == '__main__':
    ut.main()
