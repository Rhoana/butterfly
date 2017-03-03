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

    def update_source(self, keywords):
        # take named keywords
        output = self.OUTPUT.INFO
        runtime = self.RUNTIME.IMAGE
        # Unpack numpy dimensions
        Z,Y,X = keywords[output.SIZE.NAME]
        # Get the right kind of datsource
        runtime.SOURCE.VALUE = keywords[runtime.SOURCE.NAME]
        # set named keywords to self
        runtime.BLOCK.VALUE = keywords[runtime.BLOCK.NAME]
        output.TYPE.VALUE = keywords[output.TYPE.NAME]
        output.SIZE.VALUE = {
            output.SIZE.Z.NAME: int(Z),
            output.SIZE.Y.NAME: int(Y),
            output.SIZE.X.NAME: int(X)
        }
        # Optional keywords by source
        inH5 = runtime.SOURCE.HDF5.INNER
        optional_fields = [inH5, output.PATH]
        # Assign all optional keywords
        for op in optional_fields:
            op.VALUE = keywords.get(op.NAME,op.VALUE)
