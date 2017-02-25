import logging
from Settings import *
from tornado import web
from tornado import gen
from urllib2 import HTTPError
from concurrent.futures import ThreadPoolExecutor

class RequestHandler(web.RequestHandler):

    INPUT = INPUT()
    OUTPUT = OUTPUT()
    RUNTIME = RUNTIME()
    BFLY_CONFIG = BFLY_CONFIG

    def initialize(self, _core):
        self._ex = ThreadPoolExecutor(max_workers=10)
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Methods', 'GET')
        self._core = _core

    # Each Handler must define
    def parse(self, _request):
        pass

    @gen.coroutine
    def get(self, *args):
        try:
            query = self.parse(*args)
            yield self._ex.submit(self.handle, query)
        except HTTPError, http_error:
            self.set_status(http_error.code)
            self.set_header('Content-Type', "text/plain")
            self.write(http_error.msg)

    def check(self, _query):
        return _query

    def handle(self, _query):
        this_method = _query.INPUT.METHODS.VALUE
        self.set_header('Content-Type',_query.content_type)
        if _query.is_data:
            content = self._core.get_data(_query)
        else:
            content = self._core.get_info(_query)
        self.write(content)
        return content

    def log(self, action, **kwargs):
        statuses = {
            'exist': 'error',
            'check' : 'error'
        }
        actions = {
            'exist': 'Missing {term} parameter',
            'check' : 'The {term} \'{val}\' is not {check}'
        }
        status = statuses[action]
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
