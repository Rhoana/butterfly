import bfly
import unittest as ut
import datetime
import logging
import sys

class TestWebserver(ut.TestCase):
    """ set up tests for `bfly.Webserver`
    """
    PORT = 2017
    DB_PATH = None
    DB_TYPE = 'Zodb'
    RUNTIME = bfly.UtilityLayer.RUNTIME()
    # Log to the command line
    log_info = {
        'stream': sys.stdout,
        'level': logging.INFO
    }

    @classmethod
    def test_web(cls):
        """ test that `bfly.Webserver` can start and stop.
        """

        # Log to command line
        logging.basicConfig(**cls.log_info)

        # Make a dummy database
        db_class = getattr(bfly.DatabaseLayer, cls.DB_TYPE)
        db = db_class(cls.DB_PATH, cls.RUNTIME)

        # Make a dummy webserver
        config = bfly.UtilityLayer.config
        web = bfly.Webserver(db, config)
        server = web.start(cls.PORT)

        # Stop the webserver after 1 second
        one_sec = datetime.timedelta(seconds=1)
        server.add_timeout(one_sec, web.stop)

        # Start the webserver right now
        server.start()

if __name__ == '__main__':
    ut.main()
