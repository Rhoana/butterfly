from Query import Query
import numpy as np
import logging

class InfoQuery(Query):

    def __init__(self,*args,**kwargs):

        # Add basic list of getters
        self.groups = map(self.grouper, self.rankings)
        self.X,self.Y,self.Z = self.position[:3]
        self.make_getter('tile_keys', '')
        self.make_getter('data_keys', '')
        self.make_getter('info_keys', '')
        self.make_getter('position', -1)
        self.make_getter('groups', '')

        # Set all raw attributes
        concat = lambda a,b: a+getattr(self,b)
        keys = [[],'tile_keys','info_keys','data_keys']
        keys = keys + ['position','groups']
        allkeys = reduce(concat, keys)
        havekeys = set(kwargs.keys())
        for key in set(allkeys) & havekeys:
            self.raw[key] = kwargs[key]

    @property
    def key(self):
        get = lambda k: getattr(self,k)
        return '_'.join(map(get,self.groups))

    @property
    def content_type(self):
        fmt = self.att(self.FORM)
        content_type = self.content_types[0]
        return content_type.replace('{fmt}', fmt)

    @property
    def result(self):
        if self.method in self.rankings:
            return self.list
        if self.method in [self.METADATA]:
            return {
                self.PATH: getattr(self,self.PATH),
                self.TYPE: getattr(self,self.TYPE),
                'dimensions': {
                    self.X: self.x,
                    self.Y: self.y,
                    self.Z: self.z
                },
                self.NAME: self.name
            }
        return self.list

