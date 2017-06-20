from mimetypes import types_map
import tornado.ioloop
import tornado.web
import numpy as np
import json
import time
import cv2
import sys
import os

class Experiment():

    TRIALS = 10
    OUT_FMT = time.strftime('%Y_%m_%d')+'_x{}_{}x{}.json'

    MEGABYTE = 1024**2

    def __init__(self, _shape, _dtype, _levels, _tiles, _output):
        self._shape = _shape
        self._dtype = _dtype
        self._levels = _levels
        self._tiles = _tiles
        # Record number of steps
        n_tiles = len(_tiles)
        self._steps = self.TRIALS * n_tiles
        self._step = 0
        # Make the output filename
        out_file = self.OUT_FMT.format(_tiles[0], *_shape)
        self._output = os.path.join(_output, out_file)
        # Make an array to store the results
        self._results = [[] for i in range(n_tiles)]
        # Create new images
        self.new_images()

    @property
    def tile_id(self):
        # Get the tile id for this step
        n_tiles = len(self._tiles)
        return self._step % n_tiles

    def get_tile(self):
        # Get the tile id for this step
        return self._tiles[self.tile_id]

    def save_data(self, _results):
        # Get the bytes per each voxel
        voxel_bytes = np.iinfo(self._dtype).bits // 8
        # Get the total mebibytes of the slice
        full_bytes = voxel_bytes * np.prod(self._shape)
        full_mb = int(full_bytes / self.MEGABYTE)
        
        # Get the mean of the trials
        mean_times = np.mean(_results, 1)
        # Get the mean and all of the rates
        mean_rates = full_mb / mean_times
        all_rates = full_mb / np.array(_results)
        # Combine all the constants together
        output = {
            'mean_times': mean_times.tolist(),
            'mean_rates': mean_rates.tolist(),
            'all_rates': all_rates.tolist(),
            'all_times': _results,
            'tiles': self._tiles,
            'shape': self._shape,
            'levels': self._levels,
            'dtype': np.dtype(self._dtype).name,
        }
        # Write the model to json
        with open(self._output, 'w') as fd:
            json.dump(output, fd, indent=4)
        # Notify
        msg = """Done!
    Wrote {}
        """.format(self._output)
        print(msg)

    def add_step(self, _time):
        # Add time to results
        self.add_time(_time)
        # Move to the next steep
        if self._step + 1 < self._steps:
            self._step += 1
            command = "continue"
        else:
            # Save the data
            self.save_data(self._results)
            # Reset the step count
            self._step = 0
            # Kill the program
            command = "stop"
        # Create new images
        self.new_images()
        return command

    def add_time(self, time):
        # Milliseconds to seconds
        seconds = float(time) / 1000.0
        # Add the time to the results
        self._results[self.tile_id].append(seconds)

    def add_server(self, _server):
        self._server = _server

    # Create all the images
    def new_images(self):
        """ Make a volume for each resolution
        """
        vols = []
        # Get all variables
        _shape = self._shape
        _dtype = self._dtype
        _levels = self._levels
        _tile = self.get_tile()
        # Noise max value
        dmax = np.iinfo(_dtype).max
        # Define grid by even multiple of tiles
        _grid = np.floor_divide(_shape, _tile)
        # Square the tile dimensions
        tile_shape = (_tile,) * 2
        # Add a volume for each resolution
        for level in range(_levels):
            # Double the number of tiles per scale
            scale_grid = np.floor_divide(_grid, 2**level)
            # Make a volume stack of all tiles
            full_shape = np.r_[scale_grid, tile_shape]
            # Get name of data type used to make noise
            dname = np.dtype(_dtype).name
            msg = """Making {} of {} noise... for scale {}"""
            print msg.format(full_shape, dname, level)

            # Add the volume to the list of all resolutions
            vols.append(np.random.randint(0, dmax, full_shape, _dtype))
        # Return all volumes
        self._images = vols

class ExperimentHandler(tornado.web.RequestHandler):

    @property
    def _tile(self):
        return self._exp.get_tile()

    @property
    def _shape(self):
        return self._exp._shape

    @property
    def _dtype(self):
        return self._exp._dtype

    @property
    def _levels(self):
        return self._exp._levels

    @property
    def _images(self):
        return self._exp._images

    @property
    def _tile_shape(self):
        return self._images[0].shape[2:]

    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


class ImageHandler(ExperimentHandler):

    # Tile constants
    SCALE = ("scale", 0)
    X = ("x", 0)
    Y = ("y", 0)

    IMAGE_TYPE = ".png"

    # Boot constants
    REBOOT_TYPE = ".txt"
    TIME = ("time", 0)

    def initialize(self, _exp):
        # Store the expriment
        self._exp = _exp

    def get(self, request):
        # Reboot server
        if request == 'reboot':
            # Set the mime type
            mime = types_map.get(self.REBOOT_TYPE)
            # Save the given time
            time = self.get_int_query(*self.TIME)
            # Load images for the next step
            result = self._exp.add_step(time)
        # Get a tile
        else:
            # Set the mime type
            mime = types_map.get(self.IMAGE_TYPE)
            # Give the requested tile
            result = self.parse_tile()
        # Set mime type
        self.set_header("Content-Type", mime)
        # Write result
        self.write(result)

    def parse_tile(self):
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
        #print(msg)

        # Get the tile from the matrix
        tile = self._images[tile_scale][y_offset, x_offset, :, :]
        # Return the tile as a png image
        image = cv2.imencode(self.IMAGE_TYPE, tile)
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

class HTMLHandler(ExperimentHandler):

    def initialize(self, _exp, _path):
        """ Prepare to render HTML paths
        """
        # Store experiment and path
        self._exp = _exp
        self._path = _path

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

def start_server(_port, _shape, _tile, _dtype, _levels, _output):

    # Test all possible tile sizes
    min_max = np.log2([_tile, min(*_shape)])+[0, 2-_levels]
    # Create a range of tiles
    tiles = np.uint64(2**np.arange(*min_max)).tolist()

    # Create the experiment
    experiment = Experiment(_shape, _dtype, _levels, tiles, _output)

    # Serve images
    image_info = {
        "_exp": experiment,
    }
    # Serve HTML templates
    html_info = {
        "_path": os.path.join(os.getcwd(),"view"),
        "_exp": experiment,
    }
    # Serve static files
    static_info = {
        "path": os.path.join(os.getcwd(),"view"),
    }
    # Define the Web App
    web_app = tornado.web.Application([
        (r"/?()", HTMLHandler, html_info),
        (r"/(.*\.html)", HTMLHandler, html_info),
        (r"/(tile)/?.*", ImageHandler, image_info),
        (r"/(reboot)/?.*", ImageHandler, image_info),
        (r"/(.*)", tornado.web.StaticFileHandler, static_info),
    ], autoreload=True)

    # Start the Web App
    web_app.listen(_port)
    print "serving on port {}".format(_port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":

    PORT = 8487
    SHAPE = [2**12, 2**12]
    TILE = 2**8
    DTYPE = np.uint8
    LEVELS = 1

    # Results directory
    OUTPUT = '/n/coxfs01/thejohnhoffer/web_test/'

    # End if shape less than tile
    if min(*SHAPE) < TILE:
        msg = """
        Cannot divide {} into tiles of {}
        """.format(SHAPE, TILE)
        print msg
        sys.exit()
    # Make sure there aren't too many levels
    max_level = int(np.log2(min(*SHAPE) / TILE) + 1)
    # Negative of zero less than max level
    if LEVELS <= 0:
        LEVELS += max_level
    # Level may never be greater than max
    LEVELS = np.clip(LEVELS, 1, max_level)

    # Start the server
    start_server(PORT, SHAPE, TILE, DTYPE, LEVELS, OUTPUT)
