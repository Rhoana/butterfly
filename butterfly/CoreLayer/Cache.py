import logging
from pylru import lrucache
from Settings import MAX_CACHE_ENTRY
from CacheEntry import CacheEntry

class Cache(object):
    max_entry = MAX_CACHE_ENTRY

    def __init__(self):
        self.n_entry = 0
        self._sources = lrucache(self.max_entry)

    def update_size(self,key):
        entry = self._sources.peek(key)
        # update the max entries for the entry
        max_entry = entry.update_size(self.n_entry)
        self.log('update', key=key, n=max_entry)

    def get_source(self, query):
        return self._sources.get(query.key, 0)

    def add_source(self, query):
        if not self.get_source(query):
            self.n_entry = min(self.n_entry+1, self.max_entry)
            new_entry = CacheEntry(query, self.n_entry)
            # Add a new entry to the cache entries
            self._sources[query.key] = new_entry
            self.log('add_source',src=query.key)
            if self.n_entry < self.max_entry:
                # Lower the max size for each cache added
                self.log('n_entry', n_entry=self.n_entry)
                map(self.update_size, self._sources)
        return self.get_source(query)

    def add_tile(self, query, t_query, content):
        src = self.get_source(query)
        source = src if src else self.add_source(query)
        self.log('add_tile', src=query.key, id=t_query.key)
        return source.add_tile(t_query, content)

    def get_tile(self, query, t_query):
        tile = []
        src = self.get_source(query)
        if src:
            tile = src.get_tile(t_query)
        return tile

    def log(self, action, **kwargs):
        statuses = {
            'add_source': 'info',
            'add_tile': 'info',
            'n_entry': 'info',
            'update': 'info'
        }
        actions = {
            'add_source': 'Starting {src} cache',
            'add_tile': 'Adding {id} to {src} cache',
            'n_entry': 'Total {n_entry} entries in cache',
            'update': 'Entry {key} can have {n} entries'
        }
        status = statuses[action]
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
