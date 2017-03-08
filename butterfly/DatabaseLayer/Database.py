from Settings import *

class Database():

    def __init__(self, path):
        # Get the database keywords
        self.RUNTIME = RUNTIME()

    '''
    Interface for adding paths
    '''

    def add_paths(self, all_paths):
        for key,value in all_paths.iteritems():
            self.add_one_path(key, value)
        # Save to disk
        self.commit()
        return ''

    # Must be overwritten
    def add_one_path(self, key, value):
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
        k_list = self.RUNTIME.DB.TABLE.JOIN_LIST
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
    def get_path(self, key):
        return ''

    # Must be overwritten
    def get_table(self, table, path):
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, path)

    # Must be overwritten
    def get_entry(self, table, path, key, **keywords):
        k_join = self.RUNTIME.DB.JOIN.NAME
        return k_join.format(table, path)

    '''
    Interface for saving to disk
    '''
    # Must be overwritten
    def commit(self):
        return ''

