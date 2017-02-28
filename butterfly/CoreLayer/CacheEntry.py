class CacheEntry(object):
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

    @property
    def loaded_source(self):
        output = self.query.OUTPUT.INFO
        runtime = self.query.RUNTIME.IMAGE
        return {
            output.TYPE.NAME: output.TYPE.VALUE,
            runtime.BLOCK.NAME: runtime.BLOCK.VALUE,
            output.SIZE.NAME: output.SIZE.VALUE
        }
