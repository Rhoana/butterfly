from QueryLayer import InfoQuery
from RequestHandler import RequestHandler

class OCP(RequestHandler):

    def parse(self, request):

        super(OCP, self).parse(request)

        whois = self.request.remote_ip
        settings = {
            'feature': whois
        }
        return InfoQuery(**settings)
