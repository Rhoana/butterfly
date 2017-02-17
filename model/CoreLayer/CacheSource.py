from CacheTile import CacheTile

class CacheSource(object):
    def __init__(self):
        self._sources = {}
        self.max_size = 0

    def get_source(self, query):
        return self._sources.get(query.key, 0)

    def add_source(self, query):
        if not self.get_source(query):
            self._sources[query.key] = CacheTile(query)
        return self.get_source(query)

    def add_tile(self, query, t_id, content):
        src = self.get_source(query)
        source = src if src else self.add_source(query)
        return source.add_tile(t_id, content)

    def get_tile(self, query, t_id):
        src = self.get_source(query)
        return src.get_tile(t_id) if src else []

    def lose_old_tiles(self):
        return []
