from Database import Database
from ZODB import FileStorage, DB
import transaction

class Zodb(Database):
    """ Provides a :class:`Database` interface to ``ZODB``

    Arguments
    ----------
    path: str
        The file path to store and access the database
    _runtime: :class:`RUNTIME`
        Gets stored as :data:`RUNTIME`

    Attributes
    -----------
    RUNTIME: :class:`RUNTIME`
        With keywords needed to load files and use tables
    db: ZODB.DB
        Keeps all from ``add_path`` in a simple key-value store \
and contains each table as a separate ZODB key
    """

    def __init__(self, path, _runtime):
        # Create or load the database
        Database.__init__(self, path, _runtime)
        # Create or load the file storage
        self.storage = FileStorage.FileStorage(path)
        self.db = DB(self.storage)

    def add_path(self,c_path,d_path):
        """ store a link from a ``c_path`` to a ``d_path``
        Overides :meth:`Database.add_path`

        Arguments
        ----------
        c_path: str
            The path to a given channel with images
        d_path: str
            The path to the dataset with metadata files
        """
        Database.add_path(self, c_path, d_path)
        # Connect to the database
        with self.db.transaction() as connection:
            root = connection.root()
            # Map the c_path to the d_path
            root[c_path] = d_path

    def add_table(self, table, path):
        """ Add a table to the database
        Overides :meth:`Database.add_table`

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files

        Returns
        --------
        bool
            Whether the table was added correctly
        """
        table_path = Database.add_table(self, table, path)
        # Get the connection
        with self.db.transaction() as connection:
        # Create empty list with table, path name
            root = connection.root()
            root[table_path] = []
        # return the joint path
        return table_path

    def add_entry(self, table, path, entry):
        """ and a single entry to a table for a path
        Overides :meth:`Database.add_entry`

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        entry: dict
            The mapping of keys to values for the entry

        Returns
        --------
        bool
            Whether the entry was stored correctly
        """

        # Get constant keywords
        k_table = self.RUNTIME.DB.TABLE[table].KEY_LIST
        Database.add_entry(self, table, path, entry)

        # Get the connection
        with self.db.transaction() as connection:
            root = connection.root()
            # Get the collection of entries
            table_path = self.get_table(table, path)
            # Check if not unique in collection
            find_entry = {k: entry[k] for k in k_table}
            already = self.get_entry(table, path, **find_entry)
            # Update value if already exists
            if len(already):
                update_id = already[0]['__id']
                entry['__id'] = update_id
                root[table_path][update_id] = entry
                return entry
            # Add new value if not in collection
            entry['__id'] = len(root[table_path])
            root[table_path].append(entry)
            return entry

    def get_path(self, path):
        """ Map a channel path to a dataset path
        Overides :meth:`Database.get_path`

        Arguments
        ----------
        path: str
            The path to the given channel

        Returns
        --------
        str
            The dataset path for the  given ``path``
        """
        Database.get_path(self, path)
        # Get the connection
        with self.db.transaction() as connection:
            root = connection.root()
            return root.get(path, path)

    def get_table(self, table, path):
        """ Get the actual table for a given path
        Overides :meth:`Database.get_table`

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files

        Returns
        --------
        unqlite.Collection
            The requested :data:`db` ``.collection``
        """

        return Database.get_table(self, table, path)

    def get_all(self, table, path):
        """ Get all the entries in a table path
        Overides :meth:`Database.get_all`

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files

        Returns
        --------
        object or list
            A list of all entries in the table.
        """

        table_path = Database.get_all(self, table, path)
        # Get the actual collection from the name
        with self.db.transaction() as connection:
            root = connection.root()
            # Get the actual collection
            return root.get(table_path)

    def get_by_key(self, table, path, key):
        """ Get the entry for the key in the table.
        Overides :meth:`Database.get_by_key`

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        key: int
            The primary key value for any entry

        Returns
        --------
        dict
            The entry in the table for the given key.
        """

        table_path = Database.get_by_key(self, table, path, key)
        # Get the collection from the name
        with self.db.transaction() as connection:
            root = connection.root()
            # Get the actual collection
            collect = root.get(table_path)
            # Get entry from the collection
            if len(collect) < int(key):
                return {}
            return collect[int(key)]

    def get_by_fun(self, table, path, fun):
        """ Get the entries where function is true.
        Overrides :meth:`Database.get_by_fun`

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        fun: int
            The function to filter the table entries

        Returns
        --------
        list
        All entries where the function returns true
        """

        table_path = Database.get_by_fun(self, table, path, fun)
         # Get the collection from the name
        with self.db.transaction() as connection:
            root = connection.root()
            # Get the actual collection
            collect = root.get(table_path)
            # Get the entry from the collection
            return [c for c in collect if fun(c)]

    def commit(self):
        """ Save all database changes to disk.
        Overrides :meth:`Database.commit`
        """
        Database.commit(self)
        transaction.commit()
        return ''
