from Query import Query
import numpy as np
import logging

class InfoQuery(Query):

    def __init__(self,*args,**kwargs):

        # Add basic list of getters
        self.X,self.Y,self.Z = self.SPACE_LIST[:3]
        self.make_getter('TILE_LIST', '')
        self.make_getter('DATA_LIST', '')
        self.make_getter('INFO_LIST', '')
        self.make_getter('SPACE_LIST', -1)
        self.make_getter('GROUP_LIST', '')

        # Set all raw attributes
        concat = lambda a,b: a+getattr(self,b)
        keys = [[],'TILE_LIST','INFO_LIST','DATA_LIST']
        keys = keys + ['SPACE_LIST','GROUP_LIST']
        allkeys = reduce(concat, keys)
        havekeys = set(kwargs.keys())
        for key in set(allkeys) & havekeys:
            self.raw[key] = kwargs[key]

    @property
    def key(self):
        return '_'.join(map(self.att,self.GROUP_LIST))

    @property
    def content_type(self):
        fmt = self.att(self.FORM)
        content_type = self.content_types[0]
        return content_type.replace('{fmt}', fmt)

    @property
    def result(self):
        if self.att(self.METH) in self.GROUP_METH_LIST:
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

