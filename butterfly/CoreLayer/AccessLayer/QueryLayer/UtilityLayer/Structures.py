from itertools import ifilter

# For all nameless keywords
class NamelessStruct(object):
    VALUE = None
    def __init__(self,**_keywords):
        # Begin making the list
        all_list = _keywords.get('LIST',[])
        # Add other keywords to list
        for key in _keywords:
            keyval = _keywords[key]
            setattr(self,key,keyval)
            # Put all lists into list
            is_list = isinstance(keyval,list)
            more = keyval if is_list else []
            # Put all term names into list
            if hasattr(keyval, 'NAME'):
                more = [keyval.NAME]
            all_list += more
        if len(all_list):
            all_set = set(all_list)
            all_key = all_list.index
            self.LIST = sorted(all_set, key=all_key)

    def _n_get(self, name):
        children = self.__dict__.values()
        # Make sure name is the same
        def is_name(c):
            has_name = hasattr(c,'NAME')
            return has_name and c.NAME == name
        # Return None if no children have name
        return next(ifilter(is_name, children), None)

    def __getitem__(self, key):
        return self.__dict__.get(key,self._n_get(key))

    def get(self, key, default=None):
        if default is None:
            default = {}
        found = self.__getitem__(key)
        return found if found else default

    def __setitem__(self, key, value):
        item = self.__getitem__(key)
        # Set the VALUE of the item if is struct
        if item and isinstance(item, NamelessStruct):
            item.VALUE = value

    def __contains__(self, key):
        return None is self.__getitem__(key)

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

# For all keywords with names
class NamedStruct(NamelessStruct):
    NAME = None
    def __init__(self,_name,**_keywords):
        NamelessStruct.__init__(self, **_keywords)
        self.NAME = _name

