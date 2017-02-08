import time
import tornado
import tornado.gen
import tornado.web
from concurrent.futures import ThreadPoolExecutor

class Core():

  def get(self, a, b, c):

    print 'getting in there', c
    time.sleep(10)
    print 'done sleeping', c

    return 'msg to client' + c

class MainHandler(tornado.web.RequestHandler):

    def initialize(self, executor, core, webserver):
        self._executor = executor
        self._core = core
        self._webserver = webserver

    @tornado.gen.coroutine
    def get(self, uri):

        dyn = self.request.remote_ip

        #self._webserver.handle(self)
        res = yield self._executor.submit(self._core.get, a=100, b=200, c=dyn)

        self.write(res)


class WebServer:

    def __init__(self, port=8888):
        '''
        '''
        self._port = port

    def start(self, core):
        '''
        '''


        port = self._port

        webapp = tornado.web.Application([
            (r'(/bar)', MainHandler, {'executor':ThreadPoolExecutor(max_workers=10),
                                      'core':core,
                                      'webserver':self})
        ])

        webapp.listen(port, max_buffer_size=1024 * 1024 * 150000)


        tornado.ioloop.IOLoop.instance().start()


core = Core()

ws = WebServer()
ws.start(core)
