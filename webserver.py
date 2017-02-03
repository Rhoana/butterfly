import time 
import tornado
import tornado.gen
import tornado.web

# class MainHandler(tornado.web.RequestHandler):

#     def initialize(self, webserver):
#         self._webserver = webserver

#     @tornado.web.asynchronous
#     def get(self, uri):
#         '''
#         '''
        
#         #self._webserver.handle(self)
#         print 'bef', self
#         time.sleep(10)



#         print 'aft', self

# class MainHandler(tornado.web.RequestHandler):
#   def initialize(self, webserver):
#     self._webserver = webserver


#   @tornado.web.asynchronous
#   @tornado.gen.coroutine
#   def get(self, uri):
    
#     # self.write("Greetings from the instance %s!" % tornado.process.task_id())
#     print 'start', tornado.process.task_id(), self
#     time.sleep(10)
#     print 'end', tornado.process.task_id(), self
#     # self.write("2Greetings from the instance %s!" % tornado.process.task_id())

def long_blocking_function(index, sleep_time, callback):
    print ("Entering run counter:%s" % (index,))
    time.sleep(sleep_time)
    print ("Exiting run counter:%s" % (index,))
    return "Result from %d" % index


class MainHandler(tornado.web.RequestHandler):

    def initialize(self, webserver):
        self._webserver = webserver

    @tornado.gen.coroutine
    def get(self, uri):
        global counter
        counter += 1
        current_counter = str(counter)

        print ("ABOUT to spawn thread for counter:%s" % (current_counter,))
        result = yield self.executor.submit(long_blocking_function,
                                            index=current_counter,
                                            sleep_time=5)
        self.write(result)
        print ("DONE with the long function")

class WebServer:

    def __init__(self, port=3333):
        '''
        '''
        self._port = port

    def start(self):
        '''
        '''


        port = self._port

        webapp = tornado.web.Application([
            (r'(/)', MainHandler, {'webserver':self})
        ])

        webapp.listen(port, max_buffer_size=1024 * 1024 * 150000)


        tornado.ioloop.IOLoop.instance().start()


ws = WebServer()
ws.start()
