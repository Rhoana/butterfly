import time
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
        print 'starting ' + client_id
        time.sleep(4)
        done_txt = '\ndone with {ID}\n'+'-'*40
        print done_txt.replace('{ID}',client_id)
        _handler.set_header("Content-Type", "text/plain")
        _handler.write(client_id+'\n')
