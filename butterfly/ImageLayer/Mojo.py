from Datasource import Datasource

class Mojo(Datasource):
    
    @staticmethod
    def load_tile(query):

        # call superclass
        Datasource.load_tile(query)

        return None
