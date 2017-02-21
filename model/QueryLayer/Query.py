from Settings import *
import numpy as np
import logging

class Query():
    content_types = [
        'application/{fmt}',
        'image/{fmt}'
    ]
    INPUT = INPUT()
    RUNTIME = RUNTIME()
    OUTPUT = OUTPUT()

    def __init__(self,*args,**keywords):
        command = keywords[self.INPUT.METHODS.NAME]
        self.INPUT.METHODS.VALUE = command
        self.keywords = keywords
        pass

    def set_key(self,struct,key):
        field = getattr(struct, key)
        val = self.keywords.get(field.NAME,'')
        setattr(field.VALUE, key, val)

    @property
    def is_data(self):
        image_methods = self.INPUT.METHODS.IMAGE_LIST
        return self.INPUT.METHODS.VALUE in image_methods

    def log(self,action,**kwargs):
        statuses = {
            'miss': 'info'
        }
        actions ={
            'miss': 'Missing {lost} from {group}'
        }
        status = statuses[action]
        message = actions[action].format(**kwargs)
        getattr(logging, status)(message)
        return message
