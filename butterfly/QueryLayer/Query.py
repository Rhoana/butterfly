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
        # Get the right kind of datsource
        runtime.SOURCE.VALUE = keywords.get(runtime.SOURCE.NAME,None)
        # set named keywords to self
        is_size = lambda(b): isinstance(b,np.ndarray) and len(b) == 3
        runtime.BLOCK.VALUE = keywords.get(runtime.BLOCK.NAME,None)
        output.TYPE.VALUE = keywords.get(output.TYPE.NAME,None)
        # Unpack numpy dimensions
        full_size = keywords.get(output.SIZE.NAME, None)
        output.SIZE.VALUE = {
            output.SIZE.Z.NAME: int(full_size[0]),
            output.SIZE.Y.NAME: int(full_size[1]),
            output.SIZE.X.NAME: int(full_size[2])
        }
        if not runtime.SOURCE.VALUE:
            return -1
        if not output.TYPE.VALUE:
            return -2
        if not is_size(runtime.BLOCK.VALUE):
            return -3
        if not is_size(full_size):
            return -4

        # Optional keywords by source
        inner_path = runtime.SOURCE.HDF5.INNER
        optional_fields = [inner_path, output.PATH]
        # Assign all optional keywords
        for op in optional_fields:
            op.VALUE = keywords.get(op.NAME,op.VALUE)
        # Success
        return 0
