#!/usr/bin/env python
import sys
import butterfly

'''
Butterfly
EM Data server
Eagon Meng and Daniel Haehn
Lichtman Lab, 2015
'''

if __name__ == "__main__":

    port = butterfly.settings.PORT
    if len(sys.argv) == 2:
        port = sys.argv[1]

    core = butterfly.Core()

    webserver = butterfly.WebServer(core, port)
    webserver.start()
