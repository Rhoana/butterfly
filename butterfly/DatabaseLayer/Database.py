from Settings import *

class Database():

    def __init__(self, path):
        # Get the database keywords
        self.RUNTIME = RUNTIME()
        files = self.RUNTIME.DB.FILE
        tables = self.RUNTIME.DB.TABLE
        # Set some unique keys
        self._keys = {
            tables.NEURON.NAME: files.NEURON.LIST,
            tables.SYNAPSE.NAME: files.SYNAPSE.NEURON_LIST
        }

    '''
    Interface for adding paths
    '''

    def add_paths(self, all_paths):
        for c_path,d_path in all_paths.iteritems():
            self.add_one_path(c_path, d_path)
        # Save to disk
        self.commit()
        return ''

    # Must be overwritten
    def add_one_path(self, c_path, d_path):
        return ''

    '''
    Interface for adding tables
    '''

    def add_tables(self, paths):
        # Add all tables joined to paths
        map(self.add_each_table, paths)
        # Save to disk
        self.commit()
        return ''

    def add_each_table(self, path):
        # Get keywords for the database
        k_list = self.RUNTIME.DB.TABLE.LIST
        # Create all tables for the path
        for k_table in k_list:
            # Make a table from path and table name
            self.add_one_table(k_table, path)
        return ''

    # Must be overwritten
    def add_one_table(self, table, path):
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, path)

    '''
    Interface for adding entries
    '''

    def add_entries(self, table, path, entries):
        for entry in entries:
            # Add a dictionary entry
            if isinstance(entry, dict):
                self.add_one_entry(table, path, entry)
        # Save to disk
        self.commit()
        return ''

    # Must be overwritten
    def add_one_entry(self, table, path, entry):
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, path)

    '''
    Interface for getting
    '''

    # Must be overwritten
    def get_path(self, path):
        return path

    # Must be overwritten
    def get_table(self, table, path):
        real_path = self.get_path(path)
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, real_path)

    def get_entry(self, table, path, key=None, **keywords):
        # Get the necessary keywords
        files = self.RUNTIME.DB.FILE
        tables = self.RUNTIME.DB.TABLE
        # Use key if no keywords
        if not len(keywords):
            # Return all if no key
            if key is None:
                return self.get_all(table, path)
            # Filter by filter fun if callable
            if callable(key):
                return self.get_by_fun(table, path, key)
            # Filter by a secondary key
            if table == tables.NEURON.NAME:
                keywords[tables.NEURON.KEY.NAME] = key
            # Treat the key as the primary key
            else:
                return self.get_by_key(table, path, key)
        # Filter the database by keywords
        return self.get_by_keywords(table, path, **keywords)

    # Must be overwritten
    def get_all(self, table, path):
        return self.get_table(table, path)

    # Must be overwritten
    def get_by_key(self, table, path, key):
        return  self.get_table(table, path)

    # Must be overwritten
    def get_by_fun(self, table, path, fun):
        return  self.get_table(table, path)

    def get_by_keywords(self, table, path, **keys):
        values = lambda e: map(e.get, keys.keys())
        getter = lambda e: values(e) == keys.values()
        return self.get_by_fun(table, path, getter)

    '''
    Interface for saving to disk
    '''
    # Must be overwritten
    def commit(self):
        return ''

