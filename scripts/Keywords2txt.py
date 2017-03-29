import re
import yaml
import numpy as np
from bfly import UtilityLayer

yaml_setup = {
    'default_flow_style': False,
    'width': 33
}
np_setup = {
    'fmt': '%s',
    'delimiter': ' | '
}
CLASS = ['INPUT','RUNTIME','OUTPUT']

def class2yaml(it):
    """ writes a class as a yaml list
    """
    classn = CLASS[int(it)]
    classy = getattr(UtilityLayer, classn)
    unclean = yaml.dump({classn:classy()}, **yaml_setup)
    clean = re.sub('!!python.+\n','\n',unclean)
    return clean.split('\n')

def pad_lists(lists):
    """ add whitespace to printed lists
    """
    max_lines = len(max(lists,key=len))
    c_shape = (max_lines, len(lists))
    max_chars = 0
    for li in lists:
        max_chars = max(max_chars, len(max(li,key=len)))
        pad_lines = max_lines - len(li)
        li += [''] * pad_lines
    # Create empty numpy array for the text lists
    ch_a = np.chararray(c_shape,itemsize=max_chars)
    ch_a[:] = zip(*lists)
    return ch_a

line_lists = map(class2yaml, '012')
char_ar = pad_lists(line_lists)

with open('Keywords.txt', 'w') as outfile:
    padded_lists = char_ar.ljust(char_ar.itemsize, ' ')
    np.savetxt(outfile, padded_lists, **np_setup)
