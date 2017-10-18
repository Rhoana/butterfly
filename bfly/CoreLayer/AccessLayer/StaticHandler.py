import os
import posixpath
from tornado import web, gen
from mimetypes import types_map
from pkg_resources import resource_string
from concurrent.futures import ThreadPoolExecutor

class StaticHandler(web.RequestHandler):
    """ Returns static files to :data:`bfly.Webserver._webapp`

    Arguments
    ----------
    _root: __name__
        A module in the directory containing the static path

    Attributes
    -----------
    _basic_mime: str
        The default mime type for static requests
    _root: __name__
        taken from the ``_root`` argument

    :h:`Methods`

    """
    _basic_mime = 'text/plain'

    def initialize(self, _root):
        """ Create new handler for static data
        """
        self._root = _root
        self._ex = ThreadPoolExecutor(max_workers=10)
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Methods', 'GET')

    @gen.coroutine
    def get(self, path):
        """ Asynchronously call :meth:`handle` with :data:`_ex`

        Arguments
        ----------
        path: str
            the static path requested in the URL

        """
        filepath = self.parse(path)
        yield self._ex.submit(self.handle, filepath)

    def handle(self, filepath):
        """ Serves a path in the `./bfly/static` directory

        Arguments
        ----------
        path: str
            the actual path to a file on the server
        """
        extension = os.path.splitext(filepath)[1]
        # Get the mimetype from the requested extension
        mime_type = types_map.get(extension, self._basic_mime)
        self.set_header("Content-Type", mime_type)

        data = resource_string(self._root, filepath)
        self.write(data)

    def parse(self, path):
        """ Convert the requested path into a real system path

        Arguments
        ----------
        path: str
            the static path requested in the URL

        Returns
        ---------
        filepath: str
            the actual path to a file on the server
        """
        if not path:
            path = ''
        INDEX = 'index.html'
        # Turn directory to index
        if '.' not in os.path.basename(path):
            path = os.path.join(path, INDEX)
        # Get the actual path on server
        path = posixpath.normpath(path)
        filepath = os.path.join("static", path)
        print filepath
        # Deny access to any path outside static directory
        if os.path.isabs(path) or path.startswith(".."):
            return self.send_error(403)
        # Return the actual path on the server
        return filepath

