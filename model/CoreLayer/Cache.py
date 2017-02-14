from CacheSource import CacheSource
import numpy as np

class Cache(object):
    def __init__(self):
        self._sources = {}
        self.max_size = 0

    def find_source(self, query):
        return self._sources.get(query.key, 0)

    def add_source(self, query):
        self._sources[query.key] = CacheSource(query)
        return self.find_source(query)

    def get_source(self, query):
        src = self.find_source(query)
        return src if src else self.add_source(query)

    def add_tile(self, query, t_id, content):
        return get_source(query).add_tile(t_id, content)

    def get_tile(self, query, t_id):
        return get_source(query).get_tile(t_id)

    def lose_old_tiles(self):
        return 0
