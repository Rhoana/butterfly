import logging
from Settings import *
from tornado import web
from tornado import gen
from urllib2 import HTTPError
from concurrent.futures import ThreadPoolExecutor

class RequestHandler(web.RequestHandler):

    NAME = INFOTERMS[0]
    LIST = INFOTERMS[2]
    METH = INFOTERMS[1]
    FORM = TILETERMS[2]
    VIEW_LIST = VIEW_LIST
    FORMAT_LIST = FORMAT_LIST
    TEXT_FORMAT_LIST = TEXT_FORMAT_LIST
    TXT_METH_LIST = INFOMETHODS + GROUPMETHODS
    ALL_METH_LIST = INFOMETHODS + GROUPMETHODS + DATAMETHODS
    FEATUREMETHOD = INFOMETHODS[1]
    GROUP_METH_LIST = GROUPMETHODS
    DATA_METH_LIST = DATAMETHODS
    INFO_METH_LIST = INFOMETHODS
    ROOT_FEATURE = BFLY_CONFIG
    GROUP_LIST = GROUPTERMS

    def initialize(self, _core):
        self._ex = ThreadPoolExecutor(max_workers=10)
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Methods', 'GET')
        for pos in POSITION:
            setattr(RequestHandler, pos, pos)
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
        this_method = _query.method
        self.log('start', id=this_method)
        self.set_header('Content-Type',_query.content_type)
        if _query.is_data:
            content = self._core.get_data(_query)
        else:
            content = self._core.get_info(_query)
        self.log('done', id=this_method)
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
            'check' : 'The {term} \'{val}\' is not {check}',
            'done': 'Done with {id}\n'+'-'*40
        }
        status = statuses[action]
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
