import sys, collections
from .AccessLayer.QueryLayer import Utility

class Cache(object):

    def __init__(self, _runtime):
        self._max_memory = _runtime.CACHE.MAX.VALUE
        self._cache_meta = _runtime.CACHE.META.NAME
        self._cache = collections.OrderedDict()
        self._now_memory = 0

        # Get MakeLog Keyword Arguments
        self.k_size = _runtime.ERROR.SIZE.NAME
        self.k_val = _runtime.ERROR.OUT.NAME
        # Create info logger
        log_list = _runtime.ERROR.CACHE
        self.log = Utility.MakeLog(log_list).logging

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
            # Log Value over Max Cache
            self.log('MAX',**{
                self.k_val: key,
                self.k_size: value_memory
            })
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
        self._cache[key] = value
        # Log successful add
        self.log('ADD',**{
            self.k_val: key,
            self.k_size: self._now_memory
        })
        return 0

    def value_size(self, value):
        if isinstance(value,dict):
            return int(value[self._cache_meta])
        return sys.getsizeof(value)
