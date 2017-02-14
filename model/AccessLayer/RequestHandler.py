import logging
from tornado import web
from tornado import gen
from concurrent.futures import ThreadPoolExecutor

class RequestHandler(web.RequestHandler):

    def initialize(self, _core):
        self._ex = ThreadPoolExecutor(max_workers=10)
        self._core = _core

    # Each Handler must define
    def parse(self, _request):
        pass

    @gen.coroutine
    def get(self, *args):
        query = self.parse(*args)
        yield self._ex.submit(self.handle, query)

    def check(self, _query):
        return _query

    def handle(self, _query):
        client_id = _query.feature
        self.log('start',id=client_id)
        self.set_header('Content-Type',_query.content_type)
        if _query.is_data:
            content = self._core.get_data(_query)
        else:
            content = self._core.get_json(_query)
        self.log('done', id=client_id)
        self.write(content)
        return content

    def log(self, action, **kwargs):
        statuses = {
            'start': 'info',
            'exist': 'error',
            'check' : 'error',
            'done': 'info'
        }
        actions = {
            'start': 'Starting {id}',
            'exist': 'Missing {term} parameter',
            'check' : 'The {term} {val} is not {check}',
            'done': 'Done with {id}\n'+'-'*40
        }
        status = statuses[action]
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
