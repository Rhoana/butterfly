import logging

class toLog(object):
    # Make an interface to logging
    def __init__(self, statuses, actions):
        self.stats = statuses
        self.acts = actions

    # The actual logging function
    def logging(self, action, keys):
        # Get the log status and template
        status = self.stats.get(action,'error')
        template = self.acts.get(action,'Unknown')
        # Try to format the sting
        try:
            message = template.format(**keys)
        except KeyError:
            message = template
        # Log the message with a status
        getattr(logging, status)(message)
        return message
