import logging

class MakeLog(object):
    """Make an interface to logging

    Arguments
    ----------
    struct : NamelessStruct
        Member of :data:`RUNTIME.ERROR` with \
all the string templates for logging

    Attributes
    logs : NamelessStruct
        Taken from ``struct`` argument
    """
    def __init__(self, struct):
        self.logs = struct

    # The actual logging function
    def logging(self, action, **keys):
        """ Log the action and keys to a template

        Calls the logging method in :data:`logs` \
with the formatted template in :data:`logs`.

        Arguments
        ----------
        action : str
            The key in :data:`logs` giving the template
        keys : dict
            All the keys to format the template

        Returns
        --------
        str
            The formatted template
        """
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
