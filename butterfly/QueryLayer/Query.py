from Settings import *
import numpy as np
import logging

class Query():
    content_types = [
        'application/{fmt}',
        'image/{fmt}'
    ]

    def __init__(self,*args,**keywords):
        self.INPUT = INPUT()
        self.RUNTIME = RUNTIME()
        self.OUTPUT = OUTPUT()

        command = keywords.get(self.INPUT.METHODS.NAME,'')
        self.INPUT.METHODS.VALUE = command
        self.keywords = keywords
        pass

    def set_key(self,struct,key,empty=''):
        field = getattr(struct, key)
        default = getattr(field, 'VALUE')
        default = empty if default is None else default
        val = self.keywords.get(field.NAME, default)
        setattr(field, 'VALUE', val)

    @property
    def is_data(self):
        image_methods = self.INPUT.METHODS.IMAGE_LIST
        return self.INPUT.METHODS.VALUE in image_methods

    def log(self,action,**kwargs):
        statuses = {
            'miss': 'info',
            'update': 'info'
        }
        actions ={
            'miss': 'Missing {lost} from {group}',
            'update': '''Update {path}
            datatype to {dtype} and blocksize to {block}
            '''
        }
        status = statuses[action]
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
