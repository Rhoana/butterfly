#!~/venv/bfly/bin/python
import pkg_resources
import sys

sys.exit(
    pkg_resources.load_entry_point('butterfly','console_scripts','bfly')()
)