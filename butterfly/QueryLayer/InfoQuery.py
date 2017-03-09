from Query import Query
import numpy as np
import logging
import json
import yaml

class InfoQuery(Query):

    form = [
       { 'indent': 4 },
       { 'default_flow_style': False }
    ]
    write = [json.dumps, yaml.dump]

    def __init__(self,*args,**keywords):

        Query.__init__(self, **keywords)

        for key in ['NAMES','PATH','SIZE','CHANNEL']:
            self.set_key(self.OUTPUT.INFO,key)

        self.set_key(self.INPUT.INFO,'FORMAT')

    @property
    def key(self):
        return self.OUTPUT.INFO.PATH.VALUE

    @property
    def get_format(self):
        fmt_val = self.INPUT.INFO.FORMAT.VALUE
        return self.INPUT.INFO.FORMAT.LIST.index(fmt_val)

    @property
    def result(self):
        info_out = self.OUTPUT.INFO
        methods = self.INPUT.METHODS
        if methods.VALUE in methods.GROUP_LIST:
            return info_out.NAMES.VALUE
        if methods.VALUE == methods.META.NAME:
            return {
                info_out.PATH.NAME: info_out.PATH.VALUE,
                info_out.TYPE.NAME: info_out.TYPE.VALUE,
                info_out.SIZE.NAME: info_out.SIZE.VALUE,
                info_out.CHANNEL.NAME: info_out.CHANNEL.VALUE
            }
        return info_out.NAMES.VALUE

    @property
    def dump(self):
        out = self.get_format
        raw_output = self.result
        return self.write[out](raw_output,**self.form[out])

