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

config = {}
config_env = "RH_CONFIG_FILENAME"
default_config_filename = os.path.expanduser("~/.rh-config.yaml")
config_filename = os.environ.get(config_env, default_config_filename)

if os.path.exists(config_filename):
    config = yaml.safe_load(open(config_filename, "r"))

