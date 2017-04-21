from Database import Database
from ZODB import FileStorage, DB
import numpy as np
import persistent
import time

class StableList(persistent.list.PersistentList):
    """ Persistent table
    """
    def __init__(self):
        persistent.list.PersistentList.__init__(self)

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
    log: :class:`MakeLog`.``logging``
        All formats for log messages
    tables: dict
        Maps table strings to a persistent class
    """

    def __init__(self, path, _runtime):
        # Create or load the database
        Database.__init__(self, path, _runtime)
        # Map all the tables to classes
        k_tables = _runtime.DB.TABLE
        self.tables = {
            k_tables.BLOCK.NAME: StableList,
            k_tables.NEURON.NAME: StableList,
            k_tables.SYNAPSE.NAME: StableList,
        }
        # Default in-memory database
        storage = None
        if path:
            # Create or load the file storage
            storage = FileStorage.FileStorage(path)
        self.db = DB(storage)

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

    def empty_table(self, table_path):
        """ Add a table to the database \
overwriting any preexisting table.

        Arguments
        ----------
        table_path: str
            The combined path of the table
        """
        # Get the connection
        with self.db.transaction() as connection:
            # Create empty table with path name
            root = connection.root()
            # Make the correct table
            t_class = self.tables[table]
            root[table_path] = t_class()

    def add_table(self, table, path):
        """ Add a table to the database \
keeping any existing table.
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
            # Create empty table with path name
            root = connection.root()
            # If table is non-existent
            if table_path not in root:
                # Make the correct table
                t_class = self.tables[table]
                root[table_path] = t_class()
        # return the joint path
        return table_path

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
            # Get the list from the collection
            return list(root.get(table_path))

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
        # Get the actual collection
        collect = self.get_all(table, path)
        # Get the entry from the collection
        return [c for c in collect if fun(c)]

    ####
    # Override Database.add_entries
    ####
    def add_entries(self, table, path, t_keys, entries, update=1):
        """ Add an array or list of entries to a table
        Overrides :meth:`Database.add_entries`

        Arguments
        ----------
        table: str
            The category of table for the database
        path: str
            The dataset path to metadata files
        t_keys: list
            All of ``K`` keys for each row of ``entries``
        entries: numpy.ndarray or list
            ``N`` by ``K`` array or list where ``N`` is the number \
of entries to add and ``K`` is the number of keys per entry
        update: int
            1 to update old entries matching keys, and \
0 to write new entries ignoring old entries. Default 1.

        """
        # Get the name of the table
        table_path = Database.add_entries(self, table, path, t_keys, entries, update=1)

        # list or tuple to dict
        def dictionize((index, entry)):
            if hasattr(entry, '__len__'):
                d_entry = dict(zip(t_keys, entry))
                d_entry['__id'] = int(index)
                return d_entry
            return {}

        old_count = 0
        # Add any new entries
        if not update:
            # Return if no more entries than exist
            existing = self.get_all(table, path)
            if len(existing) >= len(entries):
                return []
            # Otherwise add remaining entries
            old_count = len(existing)
            entries = entries[old_count:]
        # create fully empty table
        else:
            self.empty_table(table_path)

        # Time to add entries
        start = time.time()
	count = len(entries)
        self.log('ADD', count, table)
        # Get all new id values
        id_index = np.arange(count)+ old_count
        id_entries = zip(id_index, entries)

	#####
	# Add all the entries
        #####
        # Get the database connection
        with self.db.transaction() as connection:
            root = connection.root()
            # Rewrite all the entries as dictionaries
            dict_entries = map(dictionize, id_entries)
            # Add new value if not in collection
            root[table_path] += dict_entries

	# Log diff and total time
	diff = time.time() - start
        self.log('ADDED', count, diff)
        return dict_entries
