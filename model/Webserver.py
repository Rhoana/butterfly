import time
import logging
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

        appio = {
            '_server': self
        }
        appset = {
            'autoreload': True
        }
        webapp = Application([
            (r'(/api)', API, appio),
            (r'(/ocp)', OCP, appio)
        ],**appset)

        webapp.listen(port, max_buffer_size=self.maxbuffer)
        IOLoop.instance().start()

    def handle(self,_handler,_query):
        client_id = _query.feature
        self.log('start',id=client_id)
        _handler.set_header('Content-Type',_query.content_type)
        if _query.is_data:
            content = self._core.get_data(_query)
        else:
            content = self._core.get_json(_query)
        self.log('done',id=client_id)
        _handler.set_header('Content-Type', 'text/plain')
        _handler.write(client_id+'\n')

    def log(self,action,**kwargs):
        statuses = [
            'info': ['start','done']
        ]
        actions ={
            'start': 'Starting {id}',
            'done': 'Done with {id}\n'+'-'*40
        }
        message = actions[action].format(**kwargs)
        status = next(s for s in statuses if action in s)
        getattr(logging, status)(message)
        return message
