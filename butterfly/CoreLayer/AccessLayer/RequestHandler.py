from tornado import web
from tornado import gen
from urllib2 import URLError
from .QueryLayer import Utility
from concurrent.futures import ThreadPoolExecutor

class RequestHandler(web.RequestHandler):

    INPUT = Utility.INPUT()
    OUTPUT = Utility.OUTPUT()
    RUNTIME = Utility.RUNTIME()
    BFLY_CONFIG = Utility.BFLY_CONFIG

    def initialize(self, _core, _db):
        self._ex = ThreadPoolExecutor(max_workers=10)
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Methods', 'GET')
        self._core = _core
        self._db = _db

        # Get global error strings
        errors = self.RUNTIME.ERROR
        k_check = errors.CHECK.NAME
        k_term = errors.TERM.NAME
        k_out = errors.OUT.NAME

        # Prepare info logging
        statuses = {
            'bad_check': 'info'
        }
        actions = {
            'bad_check': '''The {{{}}} {{{}}} is not {{{}}}
            '''.format(k_term, k_out, k_check)
        }
        # Create info logger
        logger = Utility.MakeLog(statuses,actions)
        self._logger = logger.logging

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
            details = u_error.args[0]
            self.set_status(int(details.get('http',500)))
            self.set_header('Content-Type', 'text/plain')
            self.write(self.log(details))

    def check(self, _query):
        return _query

    def handle(self, _query):
        this_method = _query.INPUT.METHODS.VALUE
        self.set_header('Content-Type',_query.mime_type)
        if _query.is_data:
            content = self._core.get_data(_query)
        else:
            content = self._core.get_info(_query)
        # Return content
        self.write(content)
        return content

    def log(self, detail):
        # Get error info and type
        keys = detail.get('keys',{})
        action = detail.get('error','')
        # Log error and return
        return self._logger(action,keys)
