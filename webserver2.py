import time
import tornado.web
import tornado.httpserver
import tornado.ioloop

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    
    # self.write("Greetings from the instance %s!" % tornado.process.task_id())

    print '-'*80
    print 'START'
    print 'ip', self.request.remote_ip
    print 'url', self.request.uri
    print 'process id', tornado.process.task_id()

    time.sleep(30)
    print '-'*80
    print 'END'
    print 'ip', self.request.remote_ip
    print 'url', self.request.uri
    print 'process id', tornado.process.task_id()

    # self.write("2Greetings from the instance %s!" % tornado.process.task_id())


app = tornado.web.Application([
  (r"/", MainHandler),
])

if __name__ == "__main__":
  server = tornado.httpserver.HTTPServer(app)
  server.bind(8888)
  server.start(0)  # autodetect number of cores and fork a process for each
  tornado.ioloop.IOLoop.instance().start()
