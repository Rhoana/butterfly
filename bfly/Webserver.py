from CoreLayer import UtilityLayer
from CoreLayer import AccessLayer
from CoreLayer import Core
from tornado.web import Application
from tornado.ioloop import IOLoop

class Webserver(object):
    """ Starts the :class:`CoreLayer.Core` and tornado web app.

    Sends the ``db`` argument to the new :class:`CoreLayer.Core`.

    Arguments
    -----------
    db : :data:`bfly.Butterfly._db_type`
        A fully-loaded database

    Attributes
    ------------
    _db: :data:`bfly.Butterfly._db_type`
        Taken from first argument ``db``
    _core: :class:`CoreLayer.Core`
        Also given the ``db`` argument
    RUNTIME: :class:`RUNTIME`
        Shared runtime instance with :data:`_db`

    _log: :class:`UtilityLayer.MakeLog`
        Log strings from :class:`RUNTIME` ``.ERROR.SERVER``
    _webapp: :class:`tornado.web.Application`
        Allow access to content at /api and /ocp \ 
        with :class:`API` and :class:`OCP`
    _server: :class:`tornado.web.Application.IOLoop`
        Allows us to stop the :data:`webapp`.\ 
        It is the :data:`webapp`'s IOLoop instance.\ 
        Only set after :meth:`start` starts :data:`_webapp`.

    _port: int
        Only set after port passed to :meth:`start`
    """
    #: Max bytes of memory for :data:`_webapp` 
    _maxbuffer = 1024 * 1024 * 200
    def __init__(self, db):
        # Create a core with a database
        self.RUNTIME = db.RUNTIME
        self._core = Core(db)
        self._db = db

        app_in = {
            '_core': self._core,
            '_db': self._db
        }
        app_set = {
            'autoreload': UtilityLayer.DEV_MODE
        }
        # Create the webapp with both access layers
        self._webapp = Application([
            (r'/api/(.*)', AccessLayer.API, app_in),
            (r'/ocp/(.*)', AccessLayer.OCP, app_in)
        ], **app_set)

        # Create info logger
        log_list = self.RUNTIME.ERROR.SERVER
        # Has all Webserver log strings from UtilityLayer
        self._log = UtilityLayer.MakeLog(log_list).logging

    def start(self, _port):
        """ Starts the :data:`_webapp` on the given port

        Sets two new class attributes:
            * :data:`_port` taken from the ``port`` argument
            * :data:`_server` needed to stop the :data:`_webapp`

        Arguments
        -----------
        _port: int
            The port number to serve all entry points

        Returns
        ---------
        tornado.IOLoop
            The :data:`_server` needed to stop the :data:`_webapp`

        """
        app_start = {
            'max_buffer_size': self._maxbuffer
        }
        self._port = _port
        # Keyword constants
        k_val = self.RUNTIME.ERROR.OUT.NAME
        # Begin to serve the web application
        self._webapp.listen(_port, **app_start)
        self._server = IOLoop.instance()
        self._log('START', **{k_val: _port})
        # Return the webserver
        return self._server

    def stop(self):
        """ Stops the :data:`_webapp`.

        Adds a :data:`_server``.``stop`` callback to :data:`_server`.\ 
        This stops :data:`_server`, which is \ 
        also known as the :data:`_webapp`'s IOLoop.

        Arguments
        -----------
            _port: int
                The port number to serve all entry points.\ 
                Also sets the class attribute :data:`_port`

        """

        # Ask tornado to stop
        ioloop = self._server
        ioloop.add_callback(ioloop.stop)
        # Keyword constants
        k_val = self.RUNTIME.ERROR.OUT.NAME
        self._log('STOP', **{k_val: self._port})


