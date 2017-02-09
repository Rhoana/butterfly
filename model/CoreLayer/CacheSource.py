
class CacheSource(object):
    def __init__(self):
        self._imageSource = []
        self.query = None

    def add_image(self, id, content):
        return 0

    def lose_image(self, id):
        return 0

    def load_image(self, id):
        return ""

    def lose_all(self):
        return 0

