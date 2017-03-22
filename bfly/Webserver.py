from CoreLayer import UtilityLayer
from CoreLayer import AccessLayer
from CoreLayer import Core
from tornado.web import Application
from tornado.ioloop import IOLoop

class Webserver(object):
    """ Starts the class:`CoreLayer.Core` and tornado web app.

    Attributes
    ------------
        _log : :class:`UtilityLayer.MakeLog`
            Log strings from UtilityLayer.RUNTIME.ERROR.SERVER
    """
    maxbuffer = 1024 * 1024 * 150000
    def __init__(self, db, **kwargs):
        # Create a core with a database
        self.RUNTIME = db.RUNTIME
        self._core = Core(db)
        self._db = db

        app_in = {
            '_core': self._core,
            '_db': self._db
        }
        app_set = {
            'autoreload': True
        }
        self._webapp = Application([
            (r'/api/(.*)', AccessLayer.API, app_in),
            (r'/ocp/(.*)', AccessLayer.OCP, app_in)
        ], **app_set)

        # Create info logger
        log_list = self.RUNTIME.ERROR.SERVER
        # Has all Webserver log strings from UtilityLayer
        self._log = UtilityLayer.MakeLog(log_list).logging

    def start(self,_port):
        app_start = {
            'max_buffer_size': self.maxbuffer
        }
        self._port = _port
        # Keyword constants
        k_val = self.RUNTIME.ERROR.OUT.NAME
        # Begin to serve the web application
        self._webapp.listen(_port, **app_start)
        self._server = IOLoop.instance()
        self._log('START', **{k_val: _port})
        # Return the webserver
        return self._server

    def stop(self):
        # Ask tornado to stop
        ioloop = self._server
        ioloop.add_callback(ioloop.stop)
        # Keyword constants
        k_val = self.RUNTIME.ERROR.OUT.NAME
        self._log('STOP', **{k_val: self._port})


