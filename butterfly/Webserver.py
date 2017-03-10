from CoreLayer import Core, Access
from tornado.web import Application
from tornado.ioloop import IOLoop

class Webserver(object):
    maxbuffer = 1024 * 1024 * 150000
    def __init__(self, db, **kwargs):
        # Create a core with a database
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

    def start(self,_port):
        app_start = {
            'max_buffer_size': self.maxbuffer
        }

        self._webapp.listen(_port, **app_start)
        IOLoop.instance().start()
        return self.log('start')

    def log(self, action, **kwargs):
        statuses = {
            'start': 'info',
            'end': 'info'
        }
        actions = {
            'start': 'Running server on port {port}',
            'end': 'Closed server on port {port}'
        }
        status = statuses[action]
        kwargs['port'] = self._port
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
