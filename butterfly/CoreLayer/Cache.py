import sys
import logging
import collections
from Settings import *

class Cache(object):
    RUNTIME = RUNTIME()

    def __init__(self):
        self._cache = collections.OrderedDict()
        self._max_memory = self.RUNTIME.CACHE.MAX.VALUE
        self._now_memory = 0

    def get(self, key):
        try:
            # Get the value from the cache. Add to top.
            value = self._cache.pop(key)
            self._cache[key] = value
            return value
        except KeyError:
            return []

    def set(self, key, value):
        # Add new item to cache memory count
        self._now_memory += self.value_size(value)
        try:
            self._cache.pop(key)
        except KeyError:
            while self._now_memory >= self._max_memory:
                # Remove old item from cache and memory count
                old_value = self._cache.popitem(last=False)[1]
                self._now_memory -= self.value_size(old_value)
        # Add new item to the cache
        self.log('add_query',key=key,size=self._now_memory)
        self._cache[key] = value

    def value_size(self, value):
        if isinstance(value,dict):
            cache_meta = self.RUNTIME.CACHE.META.NAME
            return int(value[cache_meta])
        return sys.getsizeof(value)

    def log(self, action, **kwargs):
        statuses = {
            'add_query': 'info'
        }
        actions = {
            'add_query': 'Adding {key} to cache. Cache now {size} bytes',
        }
        status = statuses[action]
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
