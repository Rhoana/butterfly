# -*- coding: utf-8 -*-

import os
import sys
import types
import re

###########
#
# Make changes to docstrings
#
##########

# Filter lines containting string
def filter_lines(lines, instring):
    id_list = [lines.index(l) for l in lines if instring in l]
    doc_list = [lines[a].split(' ')[-1] for a in id_list]
    doc_start = id_list[0] if doc_list else len(lines)
    # Return the line list and line start
    return [set(doc_list), doc_start]

# Add unlisted private methods
def add_methods(lines, methods):
    add_meth = '.. automethod:: {}'.format
    # get all the listed methods from the docstring
    meth_set, meth_start = filter_lines(lines, 'method:: ')
    # add all unset methods to the lines
    for method in set(methods) - meth_set:
        lines.insert(meth_start, add_meth(method))
    # add methods header for style points
    lines.insert(meth_start, ':h:`Methods`')
    lines.insert(meth_start, '')

# Add unlisted private attributes
def add_attributes(lines, attributes):
    add_att = '.. autoattribute:: {}'.format
    # get all the listed attributes from the docstring
    att_set, att_start = filter_lines(lines, 'attribute:: ')
    # add all unset attributes to the lines
    for attribute in set(attributes) - att_set:
        lines.insert(att_start, add_att(attribute))

# Add private methods and attributes
class FormatClass:

    def __init__(self, obj, lines):
        # Check if method or attribute
        def is_method(att):
            return isinstance(getattr(obj,att),types.MethodType)
        # do nothing if docstring has headings
        if any([':h:' in l for l in lines]):
            return lines
        # get all attributes starting with one underscore
        private = re.compile('(?:_[^_]+)+').match
        priv_all = filter(private, dir(obj))
        # filter out private methods vs attributes
        priv_meth = filter(is_method, priv_all)
        priv_att = set(priv_all) - set(priv_meth)
        # add unlisted attributes and methods
        add_attributes(lines, priv_att)
        add_methods(lines, priv_meth)

