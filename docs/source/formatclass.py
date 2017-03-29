# -*- coding: utf-8 -*-

import os
import sys
import types
import re

class FormatClass:
    """ Add private methods and attributes to docstrings
    """
    def __init__(self, obj, lines):
        # Check if method or attribute
        def is_method(att):
            return isinstance(getattr(obj,att),types.MethodType)
        # do nothing if docstring has headings
        if not any(':h:' in l for l in lines):
            # get all attributes starting with one underscore
            private = re.compile('(?:_[^_]+)+').match
            priv_all = filter(private, dir(obj))
            # filter out private methods vs attributes
            priv_meth = filter(is_method, priv_all)
            priv_att = set(priv_all) - set(priv_meth)
            # add unlisted attributes and methods
            self.add_attributes(lines, priv_att)
            self.add_methods(lines, priv_meth)

    @staticmethod
    def filter_lines(lines, instring):
        """ Filter lines containting string
        """
        id_list = [lines.index(l) for l in lines if instring in l]
        doc_list = [lines[a].split(' ')[-1] for a in id_list]
        doc_start = id_list[0] if doc_list else len(lines)
        # Return the line list and line start
        return [set(doc_list), doc_start]

    def add_attributes(self, lines, attributes):
        """ Add unlisted private attributes
        """
        add_att = '.. autoattribute:: {}'.format
        # get all the listed attributes from the docstring
        att_set, att_start = self.filter_lines(lines, 'attribute:: ')
        # add all unset attributes to the lines
        for attribute in set(attributes) - att_set:
            lines.insert(att_start, add_att(attribute))

    def add_methods(self, lines, methods):
        """ Add unlisted private methods
        """
        add_meth = '.. automethod:: {}'.format
        # get all the listed methods from the docstring
        meth_set, meth_start = self.filter_lines(lines, 'method:: ')
        # add all unset methods to the lines
        for method in set(methods) - meth_set:
            lines.insert(meth_start, add_meth(method))
            lines.insert(meth_start, '')
        # add methods header for style points
        if len(methods) or len(meth_set):
            lines.insert(meth_start, ':h:`Methods`')
        lines.insert(meth_start, '')


