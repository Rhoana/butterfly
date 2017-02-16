class CacheTile(object):
    def __init__(self, query):
        self._tiles = {}
        self.query = query

    def find_tile(self, t_id):
        return self._tiles.get(t_id.key, 0)

    def add_tile(self, t_id, content):
        self._tiles[t_id.key] = content
        return self.find_tile(t_id)

    def get_tile(self, t_id):
        tile = self.find_tile(t_id)
        return tile if tile else ''

    def lose_tile(self, t_id):
        return 0

    def lose_all(self):
        return 0

