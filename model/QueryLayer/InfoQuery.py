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
        return '_'.join(map(self.att,self.groups))

    @property
    def content_type(self):
        fmt = self.att(self.FORM)
        content_type = self.content_types[0]
        return content_type.replace('{fmt}', fmt)

    @property
    def result(self):
        if self.att(self.METH) in self.rankings:
            return self.att(self.LIST)
        if self.att(self.METH) in [self.METADATA]:
            return {
                self.PATH: self.att(self.PATH),
                self.TYPE: self.att(self.TYPE),
                'dimensions': {
                    self.X: self.att(self.X),
                    self.Y: self.att(self.Y),
                    self.Z: self.att(self.Z)
                },
                self.NAME: self.att(self.NAME)
            }
        return self.att(self.LIST)

