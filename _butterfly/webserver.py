import json
import os
import socket
import time
import tornado
import tornado.gen
import tornado.web
import tornado.websocket
import urllib
import urlparse
import numpy as np
import cv2
import StringIO
import zlib
import sys, traceback
from requestparser import RequestParser

class WebServerHandler(tornado.web.RequestHandler):

  def initialize(self, webserver):
    self._webserver = webserver

  @tornado.web.asynchronous
  @tornado.gen.coroutine
  def get(self, uri):
    '''
    '''
    self._webserver.handle(self)


class WebServer:

  def __init__( self, core, port=2001 ):
    '''
    '''
    self._core = core
    self._port = port

  def start( self ):
    '''
    '''

    ip = socket.gethostbyname('')
    port = self._port

    webapp = tornado.web.Application([
      
      (r'/metainfo/(.*)', WebServerHandler, dict(webserver=self)),
      (r'/data/(.*)', WebServerHandler, dict(webserver=self)),
      # (r'/(.*)', tornado.web.StaticFileHandler, dict(path=os.path.join(os.path.dirname(__file__),'../web'), default_filename='index.html'))
  
    ])

    webapp.listen(port, max_buffer_size=1024*1024*150000)

    print 'Starting webserver at \033[93mhttp://' + ip + ':' + str(port) + '\033[0m'

    tornado.ioloop.IOLoop.instance().start()

  @tornado.gen.coroutine
  def handle( self, handler ):
    '''
    '''
    content = None

    splitted_request = handler.request.uri.split('/')
    query = '/'.join(splitted_request[2:])[1:]

    if splitted_request[1] == 'metainfo':

      # content = self._core.get_meta_info(path)
      content = 'metainfo'
      content_type = 'text/html'

    #image data request
    elif splitted_request[1] == 'data':

      try:
        parser = RequestParser()
        args = parser.parse(splitted_request[2:])

        #Call the cutout method
        volume = self._core.get(*args)

        #Check if we got nothing in the case of a request outside the data with fit=True
        if volume.size == 0:
          raise IndexError('Tile index out of bounds')

        #Color mode is equivalent to segmentation color request right now
        color = parser.optional_queries['segcolor'] and parser.optional_queries['segmentation']

        #Accepted image output formats
        image_formats = ('png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp')

        #Process output
        out_dtype = np.uint8
        output_format = parser.output_format

        if output_format == 'zip' and not color:
          #Rotate out of numpy array
          volume = volume.transpose(1, 0, 2)
          zipped_data = zlib.compress(volume.astype(out_dtype).tostring('F'))

          output = StringIO.StringIO()
          output.write(zipped_data)
          content = output.getvalue()
          content_type = 'application/octet-stream'
        elif output_format in image_formats:
          if color:
            volume = volume[:,:,:,[2,1,0]]
            content = cv2.imencode('.' + output_format, volume[:,:,0,:].astype(out_dtype))[1].tostring()
          else:
            content = cv2.imencode('.' + output_format, volume[:,:,0].astype(out_dtype))[1].tostring()
          content_type = 'image/' + output_format
        else:
          content = 'Error 400: Bad request<br>Output file format not supported'
          content_type = 'text/html'

        #Show some basic statistics
        print 'Shape:', volume.shape

      except (KeyError, ValueError):
        print 'Missing query'
        content = 'Error 400: Bad request<br>Missing query'
        content_type = 'text/html'
      except IndexError:
        # traceback.print_exc(file=sys.stdout)
        print 'Out of bounds'
        content = 'Error 400: Bad request<br>Out of bounds'
        content_type = 'text/html'
      # except Exception:
      #   traceback.print_exc(file=sys.stdout)

    # invalid request
    if not content:
      content = 'Error 404: Not found'
      content_type = 'text/html'

    # handler.set_header('Cache-Control','no-cache, no-store, must-revalidate')
    # handler.set_header('Pragma','no-cache')
    # handler.set_header('Expires','0')
    handler.set_header('Access-Control-Allow-Origin', '*')
    handler.set_header('Content-Type', content_type)
    
    #Temporary check for img output
    handler.write(content)
