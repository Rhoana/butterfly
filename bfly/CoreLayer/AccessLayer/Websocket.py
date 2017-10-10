import tornado.websocket
from QueryLayer import InfoQuery
from RequestHandler import RequestHandler
from NDStore import get_config

websockets = []

class Websocket(tornado.websocket.WebSocketHandler):

    INPUT = RequestHandler.INPUT
    OUTPUT = RequestHandler.OUTPUT

    OPEN_API = [
        'token',
        'channel',
    ]
    def initialize(self, _core, _db, _config):

        self.core = _core;
        self.BFLY_CONFIG = _config

        # Get keys for interface
        format_key = self.INPUT.INFO.FORMAT.NAME
        method_key = self.INPUT.METHODS.NAME

        # Initializae empty query
        self.query = InfoQuery(**{
            method_key: 'websocket:info',
            format_key: 'json',
        }) 

    def check_origin(self, origin):
        # Allow anyone to send messages
        return True

    def open(self, request, **kwargs):
        # Get the path keywords
        args = request.split('/')
        keywords = dict(zip(self.OPEN_API, args)) 
        # Get path information from token
        config = get_config(self.BFLY_CONFIG, keywords, True)
        # Update the query with the parameters
        self.query.update_keys(config)
        # Get message from the core
        content = self.core.get_info(self.query)
        self.send(content)

        # Add to list
        if self not in websockets:
            websockets.append(self)

    def on_close(self):

        # Remove from list
        if self in websockets:
            websockets.remove(self)

    def on_message(self, message):
        pass
        # Handle message in the core
        # reply = self.core.get_websocket(self.query, message)
        # if reply:
        #   self.send(reply)

    def send(self, message):
        # Send to all in list
        for ws in websockets:
            ws.write_message(message)
