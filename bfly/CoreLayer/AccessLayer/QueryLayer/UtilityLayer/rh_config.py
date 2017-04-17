""" Loads ``config`` from the path ``config_filename``

Attributes
-------------
config_filename : str
    Tries environment variable "RH_CONFIG_FILENAME"\
    but defaults to ~/.rh-config.yaml.
config : dict
    Loaded from a yaml file at :data:`config_filename`
"""

import os
import yaml


def load(default_path = "~/.rh-config.yaml"):
    """ Load a config dictionary from a file

    Arguments
    ----------
    rh_path : str
        The path to a yaml file overriding the default\
path of "~/.rh-config.yaml". Will always be overridden by\
"RH_CONFIG_FILENAME" environment variable.

    Returns
    --------
    dict
        The dictionary containing all the config information
    """
    config_out = {}
    config_env = "RH_CONFIG_FILENAME"
    full_default = os.path.expanduser(default_path)
    config_path = os.environ.get(config_env, full_default)

    # Load the config file if exists
    if os.path.exists(config_path):
        config_out = yaml.safe_load(open(config_path, "r"))
    # Return the config file or an empty dictionary
    return config_path, config_out

config_filename, config = load()
