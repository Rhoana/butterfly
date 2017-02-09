
class Cache(object):
    def __init__(self):
        self._cacheSource = []
        self.max_size = 0

    def add_image(self, query, id, content):
        return 0

    def load_image(self, query, id):
        return ""

    def lose_old_images(self):
        return 0
