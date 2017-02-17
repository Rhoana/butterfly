import logging
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
            self.log('add_source',src=query.key)
        return self.get_source(query)

    def add_tile(self, query, t_query, content):
        src = self.get_source(query)
        source = src if src else self.add_source(query)
        self.log('add_tile', src=query.key, id=t_query.key)
        return source.add_tile(t_query, content)

    def get_tile(self, query, t_query):
        src = self.get_source(query)
        return src.get_tile(t_query) if src else []

    def lose_old_tiles(self):
        return []

    def log(self, action, **kwargs):
        statuses = {
            'add_source': 'info',
            'add_tile': 'info'
        }
        actions = {
            'add_source': 'Starting {src} cache',
            'add_tile': 'Adding {id} to {src} cache'
        }
        status = statuses[action]
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
