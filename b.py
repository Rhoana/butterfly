#!/usr/bin/env python
import os
import sys

import _butterfly

#
# entry point
#
if __name__ == "__main__":

  port = 2001
  if len(sys.argv) == 2:
    port = sys.argv[1]

  core = _butterfly.Core()
  
  webserver = _butterfly.WebServer(core, port)
  webserver.start()
