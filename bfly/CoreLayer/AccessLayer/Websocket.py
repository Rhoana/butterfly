import tornado.websocket
from QueryLayer import InfoQuery
from RequestHandler import RequestHandler
from NDStore import get_config

websockets = []

class Websocket(tornado.websocket.WebSocketHandler):

    INPUT = RequestHandler.INPUT
    RUNTIME = RequestHandler.RUNTIME
    OUTPUT = RequestHandler.OUTPUT

    OPEN_API = [
        'token',
        'channel',
    ]
    def initialize(self, _core, _db, _config):

        self.core = _core;
        self.BFLY_CONFIG = _config

        # Get keys for interface
        error_key = self.RUNTIME.IMAGE.ERROR.NAME
        format_key = self.INPUT.INFO.FORMAT.NAME
        method_key = self.INPUT.METHODS.NAME

        # Initializae empty query
        self.query = InfoQuery(**{
            method_key: 'websocket:restore',
            format_key: 'json',
            error_key: '',
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
        # Send welcome only via this websocket
        self.write_message(content)

        # Add to list
        if self not in websockets:
            websockets.append(self)

    def on_close(self):
        # Remove from list
        if self in websockets:
            websockets.remove(self)

    def on_message(self, message):
        # Get keys for interface
        method_key = self.INPUT.METHODS.NAME
        error_key = self.RUNTIME.IMAGE.ERROR.NAME
        # Get current method
        action_val = message.get('action', '')
        method_val = 'websocket:{}'.format(action_val),
        # Set the action from the message
        self.query.update_keys({
            method_key: method_val,
            error_key: '',
        })
        # Get reply from the core
        reply = self.core.get_edits(self.query, message)
        self.send(reply)

    def send(self, message):
        # Send to all in list
        for ws in websockets:
            ws.write_message(message)
