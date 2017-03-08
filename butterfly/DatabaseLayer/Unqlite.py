from Database import Database
import unqlite

class Unqlite(Database):

    def __init__(self, path):
        # Create or load the database
        self.db = unqlite.UnQLite(path)
        Database.__init__(self, path)

    '''
    Overwirting interface Setters
    '''

    def add_one_path(self,key,value):
        Database.add_one_path(self, key, value)
        self.db[key] = value
        return ''

    def add_one_table(self, table, path):
        tablepath = Database.add_one_table(self, table, path)
        # Create collection with table, path name
        collect= self.db.collection(tablepath)
        collect.create()
        return ''

    def add_one_entry(self, table, path, entry):
        Database.add_one_entry(self, table, path, entry)
        # Add the entry to the collection
        collect = self.get_table(table, path)
        collect.store(entry)
        return ''

    '''
    Custom Getters for Unqlite
    '''

    def get_by_key(self, table, path, key):
        # Get the entry from the collection
        collect = self.get_table(table, path)
        return collect.fetch(int(key))

    def get_by_function(self, table, path, function):
        # Get the entry from the collection
        collect = self.get_table(table, path)
        return collect.filter(function)

    def make_filter(self, **keys):
        values = lambda e: map(e.get, keys.keys())
        return lambda e: values(e) == keys.values()

    '''
    Override interface Getters
    '''

    def get_path(self,key):
        Database.get_path(self, key)
        return self.db[key]

    def get_table(self, table, path):
        table_path = Database.get_table(self, table, path)
        return self.db.collection(table_path)

    def get_entry(self, table, path, key='', **keywords):
        Database.get_entry(self, table, path, key, **keywords)
        # Filter by keywords if keywords
        if len(keywords):
            check = make_filter(**keywords)
            return self.get_by_function(table, path, check)
        # Filter by filter function if callable
        if callable(key):
            return self.get_by_function(table, path, key)
        # Assume key can convert to integer
        return self.get_by_key(table, path, key)

    '''
    Overwrite saving interface
    '''
    def save_all(self):
        self.db.commit()
        return ''
