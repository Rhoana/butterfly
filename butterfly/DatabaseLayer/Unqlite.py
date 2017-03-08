from Database import Database
import unqlite

class Unqlite(Database):

    def __init__(self,path):
        # Create or load the database
        self.db = unqlite.UnQLite(path)

    def get_by_function(self,function):
        Database.get_by_function(function)

        return ''

    def add_entry(self,dataset,entry):
        Database.add_entry(entry)

        return ''

    def get_by_key(self,key):
        Database.get_by_key(key)

        return ''

