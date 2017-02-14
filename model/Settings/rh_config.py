'''Configuration loader'''

import os
import yaml

config = {}
config_env = "RH_CONFIG_FILENAME"
default_config_filename = os.path.expanduser("~/.rh-config.yaml")
config_filename = os.environ.get(config_env, default_config_filename)

if os.path.exists(config_filename):
    config = yaml.safe_load(open(config_filename, "r"))

all = [config]
