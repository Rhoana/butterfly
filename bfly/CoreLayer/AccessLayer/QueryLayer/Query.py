from mimetypes import types_map
from UtilityLayer import INPUT
from UtilityLayer import RUNTIME
from UtilityLayer import OUTPUT
from urllib2 import URLError
import numpy as np

class Query():

    basic_mime = 'text/plain'

    def __init__(self,*args,**keywords):
        self.INPUT = INPUT()
        self.RUNTIME = RUNTIME()
        self.OUTPUT = OUTPUT()

        command = keywords.get(self.INPUT.METHODS.NAME,'')
        self.INPUT.METHODS.VALUE = command
        self.keywords = keywords

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

    @property
    def mime_type(self):
        info_type = self.INPUT.INFO.FORMAT.VALUE
        image_type = self.INPUT.IMAGE.FORMAT.VALUE
        # Use image type for data and info type for info
        file_type = image_type if self.is_data else info_type
        # Get the right mime tyep or use deafult for this class
        basic_mime = self.basic_mime.format(file_type)
        return types_map.get('.'+file_type, basic_mime)

    def update_source(self, keywords):
        # take named keywords
        output = self.OUTPUT.INFO
        runtime = self.RUNTIME.IMAGE
        # Get the right kind of datsource and datatype
        source_val = keywords.get(runtime.SOURCE.NAME)
        type_val = keywords.get(output.TYPE.NAME)
        # Get the right blocksize
        block = keywords.get(runtime.BLOCK.NAME)
        # Unpack dimensions for full volume
        full_size = keywords.get(output.SIZE.NAME, [0,0,0])

        # Make sure the source and type are valid
        self.check_list(runtime.SOURCE.LIST, source_val, 'source')
        self.check_list(output.TYPE.LIST, type_val, 'type')
        # Make sure the blocksize and size have len 3
        self.check_length(3, block, 'blocksize')
        self.check_length(3, full_size, 'full size')
        # Make sure size is bigger than blocksize
        msg = 'bigger than {}'.format(block)
        within = np.all(np.uint32(block) <= full_size)
        self.check_any(within, msg, full_size, 'full size')

        # Set all the clean values
        output.TYPE.VALUE = type_val
        runtime.SOURCE.VALUE = source_val
        runtime.BLOCK.VALUE = np.uint32(block)

        # Set the output size
        output.SIZE.VALUE = {
            output.SIZE.Z.NAME: int(full_size[0]),
            output.SIZE.Y.NAME: int(full_size[1]),
            output.SIZE.X.NAME: int(full_size[2])
        }

        # Optional keywords by source
        inner_path = runtime.SOURCE.HDF5.INNER
        outer_path = runtime.SOURCE.HDF5.OUTER
        optional_fields = [inner_path, outer_path]
        # Assign all optional keywords
        for op in optional_fields:
            op.VALUE = keywords.get(op.NAME,op.VALUE)

    def check_any(self,is_good,message,value,term):
        errors = self.RUNTIME.ERROR
        k_check = errors.CHECK.NAME
        k_term = errors.TERM.NAME
        k_out = errors.OUT.NAME

        if not is_good:
            self.raise_error('CHECK',{
                k_check: message,
                k_out: str(value),
                k_term: term
            })

    def check_list(self,whitelist,value,term):
        in_list = value in whitelist
        msg = 'in {}'.format(whitelist)
        self.check_any(in_list,msg,value,term)

    def check_length(self,length,value,term):
        msg0 = 'a list or array'
        has_len = hasattr(value, '__len__')
        self.check_any(has_len,msg0,value,term)

        msg1 = 'of length three'
        is_length = len(value) == length
        self.check_any(is_length,msg1,value,term)

    @staticmethod
    def raise_error(status,detail):
        raise URLError([status, 503, detail])

