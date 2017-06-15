import numpy as np
import requests

class NDA():

    BOSS="https://auth.theboss.io/auth/realms/BOSS/protocol/openid-connect/token"
    ARIADNE="https://ariadne-nda.rc.fas.harvard.edu/api/v0.1"

    def __init__(self, groups, username, password):
        """ Give all needed to make a connection
        Arguments
        ----------
        groups : list
            Three items : collection, experiment, channel
        username : str
            Username for boss authentication
        password : str
            Passsword for boss authentication
        """
        # Join the groups into the ariadne NDA url
        path = '/'.join(groups)
        self.URL = self.ARIADNE + "/{}/" + path + "/{}"

        # Need keys to get authentication string
        auth_keys = {
            "data": {
                "username": username,
                "password": password,
                "grant_type": "password",
                "client_id": "cox",
            },
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
            }
        }
        # Get authentication string
        response = requests.post(self.BOSS, **auth_keys).json()
        bearer = "bearer {}".format(response["access_token"])
        # Save resulting authorization key
        self.AUTH_KEYS = {
            "headers": {
                "Authorization": bearer,
            }
        }

    def stringify(self, arg):
        """ Convert arguments to strings
        """
        if str(arg) == arg:
            # Return strings unchanged
            return arg
        elif hasattr(arg, '__len__'):
            # Two values from argument go to list
            return "{},{}".format(*np.uint32(arg[:2]))
        else:
            # Argument becomes integer string
            return "{}".format(int(arg))

    def request(self, feature, args):
        """ Make a request for any feature
        """
        # Format the URL correctly
        query = '/'.join([self.stringify(a) for a in args])
        url = self.URL.format(feature, query)
        # Get response data from the url with authorization
        return requests.get(url, **self.AUTH_KEYS).json()

    def is_synapse(self, *args):
        """
        Arguments
        ----------
        0 : int
            Synapse ID value
        """
        # Format the URL parameters
        return self.request("is_synapse", args)

    def synapse_ids(self, *args):
        """
        Arguments
        ----------
        0 : int
            Resolution of input coordinates
        1 : list
            Input X0,X1 coordinates
        2 : list
            Input Y0,Y1 coordinates
        3 : list
            Input Z0,Z1 coordinates
        """
        # Format the URL parameters
        return self.request("synapse_ids", args)

    def synapse_keypoint(self, *args):
        """
        Arguments
        ----------
        0 : int
            Resolution of input coordinates
        1 : int
            Synapse ID value
        """
        # Format the URL parameters
        return self.request("synapse_keypoint", args)

    def synapse_parent(self, *args):
        """
        Arguments
        ----------
        0 : int
            Synapse ID value
        """
        # Format the URL parameters
        return self.request("synapse_parent", args)

    def is_neuron(self, *args):
        """
        Arguments
        ----------
        0 : int
            Neuron ID value
        """
        # Format the URL parameters
        return self.request("is_neuron", args)

    def neuron_ids(self, *args):
        """
        Arguments
        ----------
        0 : int
            Resolution of input coordinates
        1 : list
            Input X0,X1 coordinates
        2 : list
            Input Y0,Y1 coordinates
        3 : list
            Input Z0,Z1 coordinates
        """
        # Format the URL parameters
        return self.request("neuron_ids", args)

    def neuron_keypoint(self, *args):
        """
        Arguments
        ----------
        0 : int
            Resolution of input coordinates
        1 : int
            Neuron ID value
        """
        # Format the URL parameters
        return self.request("neuron_keypoint", args)

    def neuron_children(self, *args):
        """
        Arguments
        ----------
        0 : int
            Resolution of input coordinates
        1 : list
            Input X0,X1 coordinates
        2 : list
            Input Y0,Y1 coordinates
        3 : list
            Input Z0,Z1 coordinates
        4 : int
            Neuron ID value
        """
        # Format the URL parameters
        return self.request("neuron_children", args)
