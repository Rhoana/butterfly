from QueryLayer import InfoQuery
from RequestHandler import RequestHandler

class OCP(RequestHandler):
    """ Responds to :data:`bfly.Webserver._webapp` /ocp endpoint

    Attributes
    -----------
    inherits: :class:`RequestHandler`


    :h:`Methods`

    """
    def parse(self, request):
        """ Extract details from any of the methods
        Overrides :meth:`Database.parse`

        Arguments
        ----------
        request: str
            The single method requested in the URL

        Returns
        ---------
        :class:`QueryLayer.Query`
            contains standard details for each request
        """

        super(OCP, self).parse(request)

        whois = self.request.remote_ip
        settings = {
            'feature': whois
        }
        return InfoQuery(**settings)
