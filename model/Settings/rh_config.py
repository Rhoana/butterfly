'''Configuration loader'''

import os
import yaml

default_config_filename = os.path.expanduser("~/.rh-config.yaml")
config_filename = os.environ.get("RH_CONFIG_FILENAME", default_config_filename)
if os.path.exists(config_filename):
    config = yaml.safe_load(open(config_filename, "r"))
else:
    config = {}


def get_entry(defaults, *args):
    """Get a config entry
    Get a nested entry from the config file, using a default configuration
    to supply the default if the config entry is missing.
    example:
        defaults = { "foo": { "bar":"baz" } }
        get_entry(defaults, "foo", "bar")
    :param defaults: dictionary of defaults.
    """
    d = config
    for arg in args:
        if arg in d:
            d = d[arg]
        else:
            d = defaults[arg]
        defaults = defaults[arg]
    return d

all = [config, get_entry]
