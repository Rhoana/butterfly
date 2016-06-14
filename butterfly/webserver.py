import logging
import os
import pkg_resources
import socket
import tornado
import tornado.gen
import tornado.web
import tornado.websocket
import numpy as np
import cv2
import mimetypes
import posixpath
import StringIO
import zlib
import rh_logger
import settings
from requestparser import RequestParser
from urllib2 import HTTPError
from restapi import RestAPIHandler


class WebServerHandler(tornado.web.RequestHandler):

    def initialize(self, webserver):
        self._webserver = webserver

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, uri):
        '''
        '''
        self._webserver.handle(self)


#
# Thank you Luigi:
# https://github.com/spotify/luigi/blob/
#    f7219c38121098d464011a094156d99b5b320362/luigi/server.py#L212
#
# Had vague idea that resources should be served via pkg_handler and
# Luigi did it, so I am cribbing from their implementation.
#
class PkgResourcesHandler(tornado.web.RequestHandler):

    def get(self, path):
        if path == "/":
            self.redirect("index.html?"+self.request.query)
        path = posixpath.normpath(path)
        if os.path.isabs(path) or path.startswith(".."):
            return self.send_error(404)

        extension = os.path.splitext(path)[1]
        if extension in mimetypes.types_map:
            self.set_header("Content-Type", mimetypes.types_map[extension])
        data = pkg_resources.resource_string(
            __name__, os.path.join("static", path))
        self.write(data)


class WebServer:

    def __init__(self, core, port=2001):
        '''
        '''
        self._core = core
        self._port = port

    def start(self):
        '''
        '''

        ip = socket.gethostbyname('')
        port = self._port

        webapp = tornado.web.Application([
            (r'/api/(.*)', RestAPIHandler, dict(core=self._core)),
            (r'/metainfo/(.*)', WebServerHandler, dict(webserver=self)),
            (r'/data/(.*)', WebServerHandler, dict(webserver=self)),
            (r'/stop/(.*)', WebServerHandler, dict(webserver=self)),
            (r'/(index\.html)', PkgResourcesHandler, {}),
            (r'/(.*\.js)', PkgResourcesHandler, {}),
            (r'/(images/.*\.png)', PkgResourcesHandler, {}),
            (r'(/)', PkgResourcesHandler, {})

        ])

        webapp.listen(port, max_buffer_size=1024 * 1024 * 150000)
        startup_msg = ('Starting webserver at \033[93mhttp://' + ip + ':' +
                       str(port) + '\033[0m')

        rh_logger.logger.report_event(startup_msg)

        tornado.ioloop.IOLoop.instance().start()

    @tornado.gen.coroutine
    def handle(self, handler):
        '''
        '''
        content = None

        splitted_request = handler.request.uri.split('/')

        if splitted_request[1] == 'metainfo':

            # content = self._core.get_meta_info(path)
            content = 'metainfo'
            handler.set_header("Content-type", 'text/html')
        elif splitted_request[1] == 'stop':
            import tornado
            tornado.ioloop.IOLoop.instance().stop()
            handler.set_status(200)
            handler.set_header("Content-type", "text/plain")
            handler.write("stop")
            return

        # image data request
        elif splitted_request[1] == 'data':

            try:
                parser = RequestParser()
                args = parser.parse(splitted_request[2:])

                # Call the cutout method
                volume = self._core.get(*args)

                # Check if we got nothing in the case of a request outside the
                # data with fit=True
                if volume.size == 0:
                    raise IndexError('Tile index out of bounds')

                # Color mode is equivalent to segmentation color request right
                # now
                color = parser.optional_queries[
                    'segcolor'] and parser.optional_queries['segmentation']

                # Accepted image output formats
                image_formats = settings.SUPPORTED_IMAGE_FORMATS

                # Process output
                out_dtype = np.uint8
                output_format = parser.output_format

                if output_format == 'zip' and not color:
                    # Rotate out of numpy array
                    volume = volume.transpose(1, 0, 2)
                    zipped_data = zlib.compress(
                        volume.astype(out_dtype).tostring('F'))

                    output = StringIO.StringIO()
                    output.write(zipped_data)
                    content = output.getvalue()
                    content_type = 'application/octet-stream'
                elif output_format in image_formats:
                    if color:
                        volume = volume[:, :, :, [2, 1, 0]]
                        content = cv2.imencode(
                            '.' + output_format,
                            volume[
                                :,
                                :,
                                0,
                                :].astype(out_dtype))[1].tostring()
                    else:
                        content = cv2.imencode(
                            '.' + output_format,
                            volume[
                                :,
                                :,
                                0].astype(out_dtype))[1].tostring()
                    content_type = 'image/' + output_format
                else:
                    raise HTTPError(handler.request.uri,
                                    400,
                                    'Output file format not supported',
                                    [], None)

                # Show some basic statistics

                rh_logger.logger.report_event(
                    'Total volume shape: %s' % str(volume.shape))
                handler.set_header('Content-Type', content_type)

            except (KeyError, ValueError):
                rh_logger.logger.report_event('Missing query',
                                              log_level=logging.WARNING)
                content = 'Error 400: Bad request<br>Missing query'
                content_type = 'text/html'
                handler.set_status(400)
            except IndexError:
                rh_logger.logger.report_exception(msg='Could not load image')
                content = 'Error 400: Bad request<br>Could not load image'
                content_type = 'text/html'
                handler.set_status(400)
            except HTTPError, http_error:
                content = http_error.msg
                if len(http_error.hdrs) == 0:
                    handler.set_header('Content-Type', "text/html")
                handler.set_status(http_error.code)
            # except Exception:
            #   traceback.print_exc(file=sys.stdout)

        # invalid request
        if not content:
            handler.set_status(404)
            content = 'Error 404: Not found'
            handler.set_header("Content-Type", 'text/html')

        # handler.set_header('Cache-Control',
        #                    'no-cache, no-store, must-revalidate')
        # handler.set_header('Pragma','no-cache')
        # handler.set_header('Expires','0')
        handler.set_header('Access-Control-Allow-Origin', '*')

        # Temporary check for img output
        handler.write(content)
