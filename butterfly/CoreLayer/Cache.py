import sys
import logging
import collections

class Cache(object):

    def __init__(self, _runtime):
        self._max_memory = _runtime.CACHE.MAX.VALUE
        self._cache_meta = _runtime.CACHE.META.NAME
        self._cache = collections.OrderedDict()
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
        value_memory = self.value_size(value)
        # Do not cache if value more than total memory
        if value_memory > self._max_memory:
            self.log('too_big',key=key,size=value_memory)
            return -1
        # Add new item to cache memory count
        self._now_memory += value_memory
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
        return 0

    def value_size(self, value):
        if isinstance(value,dict):
            return int(value[self._cache_meta])
        return sys.getsizeof(value)

    def log(self, action, **kwargs):
        statuses = {
            'add_query': 'info',
            'too_big': 'warning'
        }
        actions = {
            'add_query': 'Adding {key} to cache. Cache now {size} bytes',
            'too_big': 'Cannot cache {key}. {size} bytes is too big.'
        }
        status = statuses[action]
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
