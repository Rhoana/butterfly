import urlparse
import os
import re
from rh_logger import logger
import urllib
import settings


class RequestParser(object):

    def __init__(self):
        self.output_format = settings.DEFAULT_OUTPUT

        # Optional queries
        self.optional_queries = {}
        self.optional_query_list = ('segcolor', 'fit')
        self.assent_list = settings.ASSENT_LIST

        # Set these to false in case we use OCP format or some other format
        # that doesn't support optional parameters
        for query in self.optional_query_list:
            self.optional_queries[query] = False

    def parse(self, request):
        # Open connectome project format
        if 'ocp' in request:
            # Parse OCP request by the '/' splitted request, ind finds the
            # position of '/ocp/'
            ind = request.index('ocp')
            datapath = '/'.join(filter(None, request[:ind]))

            # Check for windows systems and undo separator changes in request
            if re.match('[a-zA-Z]:', datapath):
                datapath = os.sep.join(datapath.split('/'))
            else:
                datapath = os.sep + datapath

            # Get rid of %20 and other url escapes
            datapath = urllib.unquote(datapath)

            try:
                # Debug output in console for OCP request
                logger.report_event('OCP request: ' + str(request[ind:]))
                logger.report_event('Datapath: ' + datapath)

                w = int(float(request[ind + 2]))
                x_range = [int(i) - 1 for i in request[ind + 3].split(',')]
                y_range = [int(i) - 1 for i in request[ind + 4].split(',')]
                z_range = [int(i) - 1 for i in request[ind + 5].split(',')]
                start = [x_range[0], y_range[0], z_range[0]]
                volsize = [
                    x_range[1] - x_range[0],
                    y_range[1] - y_range[0],
                    z_range[1] - z_range[0]]

                self.output_format = request[ind + 1]
                if self.output_format == 'xy':
                    # Match OCP's image cutout service, use default image
                    # format
                    self.output_format = 'png'
            except IndexError:
                # Convert index errors in OCP format to key errors of the
                # standard query
                raise KeyError('Missing query')

        # Standard butterfly query scheme
        else:
            # Parse standard queries using urlparse
            query = '/'.join(request)[1:]
            parsed_query = urlparse.parse_qs(query)

            # Console output for parsed query
            logger.report_event('Parsed query: ' + repr(parsed_query))

            # Parse essential parameters
            datapath = parsed_query['datapath'][0]
            start = [int(a) for a in parsed_query['start'][0].split(',')]
            volsize = [int(a) for a in parsed_query['size'][0].split(',')]

            # Consider default zoom to be zero
            try:
                w = int(float(parsed_query['mip'][0]))
            except KeyError:
                w = 0

            # Try to get optional parameters
            try:
                self.output_format = parsed_query['output'][0]
            except KeyError:
                pass

            # Grab optional yes/no queries
            for query in self.optional_query_list:
                try:
                    tmp = parsed_query[query][0]
                    if tmp.lower() in self.assent_list:
                        self.optional_queries[query] = True
                except KeyError:
                    pass

        self.output_format = self.output_format.lstrip('.').lower()

        self.optional_queries['w'] = w;
        return [ datapath, start, volsize, self.optional_queries]
