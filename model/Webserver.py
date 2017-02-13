from CoreLayer import Core
from AccessLayer import API
from AccessLayer import OCP
from tornado.web import Application
from tornado.ioloop import IOLoop

class Webserver(object):
    maxbuffer = 1024 * 1024 * 150000
    def __init__(self,_port,**kwargs):
        database = kwargs.get('dname','mongo')
        self._core = Core(database)
        port = _port

        app_in = {
            '_core': self._core
        }
        app_set = {
            'autoreload': True
        }
        webapp = Application([
            (r'(/api)', API, app_in),
            (r'(/ocp)', OCP, app_in)
        ], **app_set)

        webapp.listen(port, max_buffer_size=self.maxbuffer)
        IOLoop.instance().start()
