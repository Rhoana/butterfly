from CacheTile import CacheTile

class CacheSource(object):
    def __init__(self):
        self._sources = {}
        self.max_size = 0

    def find_source(self, query):
        return self._sources.get(query.key, 0)

    def add_source(self, query):
        self._sources[query.key] = CacheTile(query)
        return self.find_source(query)

    def get_source(self, query):
        src = self.find_source(query)
        return src if src else self.add_source(query)

    def add_tile(self, query, t_id, content):
        return self.get_source(query).add_tile(t_id, content)

    def get_tile(self, query, t_id):
        return self.get_source(query).get_tile(t_id)

    def lose_old_tiles(self):
        return 0
