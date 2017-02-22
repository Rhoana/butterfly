from Query import Query
import numpy as np
import logging
import json
import yaml

class InfoQuery(Query):

    groups = []

    def __init__(self,*args,**keywords):

        Query.__init__(self, **keywords)

        metadata_list = ['NAMES','PATH','CHANNEL']
        for key in metadata_list:
            self.set_key(self.OUTPUT.INFO,key)

        self.set_key(self.INPUT.INFO,'FORMAT')
        self.set_key(self.OUTPUT.INFO,'SIZE')

        for g in self.INPUT.GROUP_LIST:
            self.groups.append(keywords.get(g,''))

        # Text format terms given explicitly
        json_name, yaml_name = self.INPUT.INFO.FORMAT.LIST[:2]

        self.formats = {
            json_name: {
                'terms': {
                    'indent': 4
                },
                'writer': json.dumps,
                'content': json_name
            },
            yaml_name: {
                'terms': {
                    'default_flow_style': False
                },
                'writer': yaml.dump,
                'content': yaml_name
            }
        }

    @property
    def key(self):
        return '_'.join(self.groups)

    @property
    def get_format(self):
        fmt = self.INPUT.INFO.FORMAT.VALUE
        return self.formats[fmt]

    @property
    def content_type(self):
        content = self.get_format['content']
        content_type = self.content_types[0]
        return content_type.replace('{fmt}', content)

    @property
    def result(self):
        info_out = self.OUTPUT.INFO
        methods = self.INPUT.METHODS
        if methods.VALUE in methods.GROUP_LIST:
            return info_out.NAMES.VALUE
        if methods.VALUE == methods.INFO_LIST[0]:
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
        return out['writer'](raw_output,**out['terms'])

