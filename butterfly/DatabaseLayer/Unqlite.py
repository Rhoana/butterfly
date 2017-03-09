from Database import Database
import unqlite

class Unqlite(Database):

    def __init__(self, path):
        # Create or load the database
        self.db = unqlite.UnQLite(path)
        Database.__init__(self, path)

    '''
    Overwriting interface Setters
    '''

    def add_one_path(self,c_path,d_path):
        Database.add_one_path(self, c_path, d_path)
        self.db[c_path] = d_path
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
    Override interface Getters
    '''
    def get_path(self, path):
        Database.get_path(self, path)
        return self.db[path] if path in self.db else path

    def get_table(self, table, path):
        table_path = Database.get_table(self, table, path)
        return self.db.collection(table_path)

    def get_all(self, table, path):
        collect = Database.get_all(self, table, path)
        return collect.all()

    def get_by_key(self, table, path, key):
        collect = Database.get_by_key(self, table, path, key)
        # Get the entry from the collection
        return collect.fetch(int(key))

    def get_by_fun(self, table, path, fun):
        collect = Database.get_by_fun(self, table, path, fun)
        # Get the entry from the collection
        return collect.filter(fun)

    '''
    Overwrite saving interface
    '''
    def commit(self):
        Database.commit(self)
        self.db.commit()
        return ''
