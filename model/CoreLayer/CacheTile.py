class CacheTile(object):
    def __init__(self, query):
        self._tiles = {}
        self.query = query

    def add_tile(self, t_id, content):
        self._tiles[t_id.key] = content
        return self.get_tile(t_id)

    def get_tile(self, t_id):
        return self._tiles.get(t_id.key, [])

    def lose_tile(self, t_id):
        return []

    def lose_all(self):
        return []

