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

    def check_synapse(self, id):
        """ Get neuron pairs and coordinates
        """
        # Get the resolution and the scale
        res = 0
        sc = 0.5**res
        scales = np.array([sc, sc, 1])
        # If synapse exists
        if self.is_synapse(id):
            # Get the neuron pairs
            parents = self.synapse_parent(id)['parent_neurons']
            # Reverse the dictionary
            parents = {i[1]:i[0] for i in parents.items()}
            # If bidirectionl synapse
            if 3 in parents:
                neurons = [parents[3], parents[3]]
            # If two neuron parents
            else:
                neurons = [parents[1], parents[2]]
            # Get the synapse coordinates
            keypoint = self.synapse_keypoint(res, id)['keypoint']
            full_keypoint = np.uint64(keypoint / scales).tolist()
            # Return all neuron ids and cooridnates
            return np.uint64(neurons + full_keypoint)
        # Return nothing if non-existent
        return np.uint64([])

    def check_bounds(self, keypoint):
        """ Get synapse ids in bounds
        """
        # Get the resolution and the scale
        res = 2
        sc = 0.5**res
        scale = np.array([sc, sc])
        scales = np.array([scale, scale, [1,1]])
        # Get the full-resolution bounds
        bounds = np.c_[keypoint,keypoint]+[0,1/sc]
        # Get the scaled bounds
        bounds = np.uint32(bounds * scales)
        
        # Get the synapses in bounds
        id_list = self.synapse_ids(res, *bounds)['ids']
        # Return list of synapses
        return id_list

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
