import logging

class MakeLog(object):
    # Make an interface to logging
    def __init__(self, struct):
        self.logs = struct

    # The actual logging function
    def logging(self, action, **keys):
        # Get the log status and template
        field = self.logs.get(action,{})
        status = field.get('LOG','error')
        template = field.get('ACT','Error')
        # Try to format the string
        try:
            message = template.format(**keys)
        except KeyError:
            message = template
        # Log the message with a status
        getattr(logging, status)(message)
        return message
