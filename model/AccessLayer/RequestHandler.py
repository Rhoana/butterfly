from tornado import web
from tornado import gen
from concurrent.futures import ThreadPoolExecutor

class RequestHandler(web.RequestHandler):

    def initialize(self, _server):
        self._ex = ThreadPoolExecutor(max_workers=10)
        self._server = _server

    # Each Handler must define
    def parse(self, _request):
        pass

    @gen.coroutine
    def get(self, *args):
        handle = self._server.handle
        query = yield self._ex.submit(self.parse, *args)
        yield self._ex.submit(handle, self, query)

    def check(self, _query):
        return _query
