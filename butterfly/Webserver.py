from CoreLayer import Utility
from CoreLayer import Core, Access
from tornado.web import Application
from tornado.ioloop import IOLoop

class Webserver(object):
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
            (r'/api/(.*)', Access.API, app_in),
            (r'/ocp/(.*)', Access.OCP, app_in)
        ], **app_set)

        # Create info logger
        log_list = self.RUNTIME.ERROR.SERVER
        self.log = Utility.MakeLog(log_list).logging

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
        self.log('START', **{k_val: _port})
        # Return the webserver
        return self._server

    def stop(self):
        # Ask tornado to stop
        ioloop = self._server
        ioloop.add_callback(ioloop.stop)
        # Keyword constants
        k_val = self.RUNTIME.ERROR.OUT.NAME
        self.log('STOP', **{k_val: self._port})


