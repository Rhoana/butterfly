import time
import logging
from CoreLayer import Core
from AccessLayer import API
from AccessLayer import OCP
from tornado.web import Application
from tornado.ioloop import IOLoop

class Webserver(object):
    maxbuffer = 1024 * 1024 * 150000
    def __init__(self,_port):
        self._core = Core()
        port = _port

        appio = {
            '_server': self
        }
        webapp = Application([
            (r'(/api)', API, appio),
            (r'(/ocp)', OCP, appio)
        ])

        webapp.listen(port, max_buffer_size=self.maxbuffer)
        IOLoop.instance().start()

    def handle(self,_handler,_query):
        client_id = _query.raw['feature']
        self.log('start',id=client_id)
        time.sleep(4)
        self.log('done',id=client_id)
        _handler.set_header("Content-Type", "text/plain")
        _handler.write(client_id+'\n')

    def log(self,action,**kwargs):
        def start(kwargs):
            c_id = kwargs['id']
            start_log = 'Starting {ID}'
            started = start_log.replace('{ID}',c_id)
            logging.info(started)
        def done(kwargs):
            c_id = kwargs['id']
            done_log = 'done with {ID}\n'+'-'*40
            is_done = done_log.replace('{ID}',c_id)
            logging.info(is_done)
        actions ={
            'start':start,
            'done':done
        }
        actions[action](kwargs)
