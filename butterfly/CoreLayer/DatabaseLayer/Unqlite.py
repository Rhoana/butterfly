from Database import Database
import unqlite

class Unqlite(Database):

    def __init__(self, path, _runtime):
        # Create or load the database
        Database.__init__(self, path, _runtime)
        self.db = unqlite.UnQLite(path)

    '''
    Overwriting interface Setters
    '''

    def add_path(self,c_path,d_path):
        Database.add_path(self, c_path, d_path)
        self.db[c_path] = d_path

    def add_table(self, table, path):
        tablepath = Database.add_table(self, table, path)
        # Create collection with table, path name
        collect= self.db.collection(tablepath)
        collect.create()
        return tablepath

    def add_entry(self, table, path, entry):
        # Get constant keywords
        k_table = self.RUNTIME.DB.TABLE[table].KEY_LIST
        Database.add_entry(self, table, path, entry)
        # Get the collection
        collect = self.get_table(table, path)
        # Check if not unique in collection
        find_entry = {k: entry[k] for k in k_table}
        already = self.get_entry(table,path,**find_entry)
        # Update value if already exists
        if len(already):
            return collect.update(already[0]['__id'], entry)
        # Add new value if not in collection
        return collect.store(entry)

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
