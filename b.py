#!/usr/bin/env python
import sys
import _butterfly

'''
Butterfly
EM Data server
Eagon Meng and Daniel Haehn
Lichtman Lab, 2015
'''

if __name__ == "__main__":

    port = _butterfly.settings.PORT
    if len(sys.argv) == 2:
        port = sys.argv[1]

    core = _butterfly.Core()

    webserver = _butterfly.WebServer(core, port)
    webserver.start()
