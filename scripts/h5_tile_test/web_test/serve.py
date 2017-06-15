from mimetypes import types_map
import tornado.ioloop
import tornado.web
import numpy as np
import time
import cv2
import sys
import os

class BootHandler(tornado.web.RequestHandler):

    FORMAT = '.txt'

    def initialize(self):
        pass

    def get(self, request):
        # Set the mime type and no cache
        mime = types_map.get(self.FORMAT)
        self.set_header("Content-Type", mime)
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        # Parse result
        self.write(self.parse())

    def parse(self):
        return 'hi'

class ImageHandler(tornado.web.RequestHandler):

    SCALE = ("scale", 0)
    X = ("x", 0)
    Y = ("y", 0)

    FORMAT = ".png"

    def initialize(self, _images):

        self._images = _images
        self._tile_shape = _images[0].shape[2:]

    def get(self, request):
        # Set the mime type and no cache
        mime = types_map.get(self.FORMAT)
        self.set_header("Content-Type", mime)
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        # Parse result
        self.write(self.parse())

    def parse(self):
        """ Get a tile at a scaled X,Y offset
        """
        # Get the tile size and scale
        tile_scale = self.get_int_query(*self.SCALE)
        # Get the x and y offsets
        x_offset = self.get_int_query(*self.X)
        y_offset = self.get_int_query(*self.Y)

        # Log the currently loading tile
        msg = """Loading a {}px tile at {},{}
        at resolution {}
        """.format(self._tile_shape, y_offset, x_offset, tile_scale)
        # print(msg)

        # Get the tile from the matrix
        tile = self._images[tile_scale][y_offset, x_offset, :, :]
        # Return the tile as a png image
        image = cv2.imencode(self.FORMAT, tile)
        return image[1].tostring()

    def get_int_query(self, name, default):
        """ Get integer argument from query string
        """
        result = self.get_query_argument(name, default)
        try:
            return int(result)
        except (TypeError, ValueError):
            msg = """
            The {} {} is not an integer.
            """.format(name, result)
            raise tornado.web.HTTPError(400, msg)

class HTMLHandler(tornado.web.RequestHandler):

    def initialize(self, _path, _tile, _shape, _levels):
        """ Prepare to render HTML paths
        """
        # Store the tile width and base path
        self._path = _path
        self._tile = _tile
        # Store the full shape and number of levels
        self._shape = _shape
        self._levels = _levels

    def get(self, request):
        if not request:
            request = 'index.html'
        # Join request to parent path
        path = os.path.join(self._path, request)
        # Render the html page
        keywords = {
            'TILE_WIDTH': self._tile,
            'FULL_WIDTH': self._shape[1],
            'FULL_HEIGHT': self._shape[0],
            'MAX_LEVEL': self._levels - 1,
            'TIME': int(time.time() * 1000),
        }
        self.render(path, **keywords)

    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

def start_server(_port, _tile, _shape, _levels):

    BITS = 8
    DTYPE = np.uint8
    # Noise max value
    DMAX = 2 ** BITS

    def make_app():

        # Define grid by even multiple of tiles
        grid_size = np.floor_divide(_shape, _tile)

        # Create the full images
        def full_images(_grid):
            """ Make a volume for each resolution
            """
            vols = []
            # Square the tile dimensions
            tile_shape = (_tile,) * 2
            # Add a volume for each resolution
            for level in range(_levels):
                # Double the number of tiles per scale
                scale_grid = np.floor_divide(_grid, 2**level)
                # Make a volume stack of all tiles
                full_shape = np.r_[scale_grid, tile_shape]
                msg = """Making {} of {} noise... for scale {}"""
                print msg.format(full_shape, DTYPE, level)

                # Add the volume to the list of all resolutions
                vols.append(np.random.randint(0, DMAX, full_shape, DTYPE))
            # Return all volumes
            return vols

        # For rebooting
        boot_info = {
        }
        # Serve images
        image_info = {
            "_images": full_images(grid_size)
        }
        # Serve HTML templates
        html_info = {
            "_path": os.path.join(os.getcwd(),"view"),
            "_levels": _levels,
            "_shape": _shape,
            "_tile": _tile,
        }
        # Serve static files
        static_info = {
            "path": os.path.join(os.getcwd(),"view"),
        }
        # Define the Web App
        return tornado.web.Application([
            (r"/?()", HTMLHandler, html_info),
            (r"/(.*\.html)", HTMLHandler, html_info),
            (r"/tile/?()", ImageHandler, image_info),
            (r"/reboot/?()", BootHandler, boot_info),
            (r"/(.*)", tornado.web.StaticFileHandler, static_info),
        ], autoreload=True)

    # Start the Web App
    make_app().listen(_port)
    print "serving on port {}".format(_port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":

    PORT = 8383
    TILE = 2**8
    SHAPE = [2**12, 2**12]
    LEVELS = 3
    # End if shape less than tile
    if min(*SHAPE) < TILE:
        msg = """
        Cannot divide {} into tiles of {}
        """.format(SHAPE, TILE)
        print msg
        sys.exit()
    # Make sure there aren't too many levels
    ratio = int(np.log2(min(*SHAPE) / TILE) + 1)
    LEVELS = min(max(1, LEVELS), ratio)

    # Start the server
    start_server(PORT, TILE, SHAPE, LEVELS)
