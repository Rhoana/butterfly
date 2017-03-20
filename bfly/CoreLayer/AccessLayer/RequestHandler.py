from tornado import web
from tornado import gen
from urllib2 import URLError
from QueryLayer import UtilityLayer
from concurrent.futures import ThreadPoolExecutor

class RequestHandler(web.RequestHandler):

    INPUT = UtilityLayer.INPUT()
    OUTPUT = UtilityLayer.OUTPUT()
    RUNTIME = UtilityLayer.RUNTIME()
    BFLY_CONFIG = UtilityLayer.BFLY_CONFIG

    def initialize(self, _core, _db):
        self._ex = ThreadPoolExecutor(max_workers=10)
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Methods', 'GET')
        self._core = _core
        self._db = _db

        # Create info logger
        log_list = self.RUNTIME.ERROR.REQUEST
        self.log = UtilityLayer.MakeLog(log_list).logging

    # Each Handler must define
    def parse(self, _request):
        pass

    @gen.coroutine
    def get(self, *args):
        try:
            query = self.parse(*args)
            yield self._ex.submit(self.handle, query)
        except URLError, u_error:
            # Get error information
            action, status, details = u_error.args[0]
            self.set_status(int(status))
            self.set_header('Content-Type', 'text/plain')
            self.write(self.log(action, **details))

    def handle(self, _query):
        self.set_header('Content-Type',_query.mime_type)
        if _query.is_data:
            content = self._core.get_data(_query)
        else:
            content = self._core.get_info(_query)
        # Return content
        self.write(content)
        return content
