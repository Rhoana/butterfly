import numpy as np
import requests
import json


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
        # Save resulting authorization key
        self.AUTH_KEYS = {
            "headers": {
                "Authorization": response["access_token"],
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
        
    def is_synapse(self, *args):
        """ 
        Arguments
        ----------
        0 : int
            Synapse ID value
        """
        # Format the URL parameters
        query = '/'.join([self.stringify(a) for a in args])
        url = self.URL.format("is_synapse", query)
        # Get the data 
        print url
        response = requests.get(url, self.AUTH_KEYS).json()
        print response

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
        query = '/'.join([self.stringify(a) for a in args])
        url = self.URL.format("synapse_ids", query)

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
        query = '/'.join([self.stringify(a) for a in args])
        url = self.URL.format("synapse_keypoint", query)

    def synapse_parent(self, *args):
        """ 
        Arguments
        ----------
        0 : int
            Synapse ID value
        """
        # Format the URL parameters
        query = '/'.join([self.stringify(a) for a in args])
        url = self.URL.format("synapse_parent", query)

    def is_neuron(self, *args):
        """ 
        Arguments
        ----------
        0 : int
            Neuron ID value
        """
        # Format the URL parameters
        query = '/'.join([self.stringify(a) for a in args])
        url = self.URL.format("is_neuron", query)

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
        query = '/'.join([self.stringify(a) for a in args])
        url = self.URL.format("neuron_ids", query)

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
        query = '/'.join([self.stringify(a) for a in args])
        url = self.URL.format("neuron_keypoint", query)

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
        query = '/'.join([self.stringify(a) for a in args])
        url = self.URL.format("neuron_children", query)
