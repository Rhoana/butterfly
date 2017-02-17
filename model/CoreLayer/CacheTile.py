class CacheTile(object):
    def __init__(self, query):
        self._tiles = {}
        self.query = query

    def add_tile(self, t_query, content):
        self._tiles[t_query.key] = content
        return self.get_tile(t_query)

    def get_tile(self, t_query):
        return self._tiles.get(t_query.key, [])

    def lose_tile(self, t_query):
        return []

    def lose_all(self):
        return []

