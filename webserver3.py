#!/usr/bin/env python

import tornado.web
import tornado.gen
import time
from functools import partial
import os
from concurrent.futures import ThreadPoolExecutor


def long_blocking_function(index, sleep_time):
    print "Entering run counter:%s" % (index,)
    time.sleep(sleep_time)
    print "Exiting run counter:%s" % (index,)
    return ('Keyyyyy' + index + '\n')


class BarHandler(tornado.web.RequestHandler):

    counter = 0

    def initialize(self, executor):
        self.executor = executor

    @tornado.gen.coroutine
    def get(self):

        global counter
        BarHandler.counter += 1
        current_counter = str(BarHandler.counter)
        print ("ABOUT to spawn thread for counter:%s" % (current_counter,))

        # Submit a task to run using the ThreadPoolExecutor. At this point we
        # give control back to Tornado, and it won't come back to us until the
        # task has finished or failed. Either way, it doesn't block because
        # we've handed control back. That's what the yield is doing.
        future_result = yield self.executor.submit(long_blocking_function,
                                              index=current_counter,
                                              sleep_time=5)

        # If we get here, then the long running function has either finished
        # or failed.
        print ("DONE executing thread for long function")
        self.write(future_result)


class Application(tornado.web.Application):
    def __init__(self):
        # Create the ThreadPoolExecutor here - we only want one of them.
        handlers = [(r"/bar", BarHandler, dict(executor=ThreadPoolExecutor(max_workers=10))),
                    ]

        settings = dict(
            debug=True,
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    application = Application()
    application.listen(8888)

    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    print """\
Starting server.
To test, use multiple invocations of curl. Browsers sometimes queue up requests
to the same URL which makes it look like your program isn't working.
Assuming curl is installed and is on your path, you would type this:
$ curl -i http://localhost:8888/bar
Good luck!
"""

    main()