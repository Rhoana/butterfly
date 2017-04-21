from Database import Database
import unqlite

class Unqlite(Database):
    """ Provides a :class:`Database` interface to ``unqlite``

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
    db: unqlite.UnQLite
        Keeps all from ``add_path`` in a simple key-value store \
and contains each tables as a separate unqlite.Collection
    log: :class:`MakeLog`.``logging``
        All formats for log messages
    """

    def __init__(self, path, _runtime):
        # Create or load the database
        Database.__init__(self, path, _runtime)
        self.db = unqlite.UnQLite(path)

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
        self.db[c_path] = d_path

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
        tablepath = Database.add_table(self, table, path)
        # Create collection with table, path name
        collect= self.db.collection(tablepath)
        collect.create()
        return tablepath

    def add_entry(self, table, path, entry, update=1):
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
        update: int
            1 to update old entries matching keys, and \
0 to write new entries ignoring old entries. Default 1.

        Returns
        --------
        dict
            The value of the entry
        """

        # Get constant keywords
        k_table = self.RUNTIME.DB.TABLE[table].KEY_LIST
        Database.add_entry(self, table, path, entry, update)
        # Get the collection
        collect = self.get_table(table, path)
        # Check if not unique in collection
        if update and self.check_keys(entry):
            # Return the entry if updated
            return entry
        # Add new value if not in collection
        collect.store(entry)
        return entry

    def check_keys(self, table, path, entry):
        """ Checks duplicate combinations of keys

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
            whether entry updates an old entry
        """
        # Get the collection
        collect = self.get_table(table, path)
        # Check if not unique in collection
        find_entry = {k: entry[k] for k in k_table}
        already = self.get_entry(table,path,**find_entry)
        # Update value if already exists
        if len(already):
            old_id = already[0]['__id']
            collect.update(old_id, entry)
            return True
        return False

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
        return self.db[path] if path in self.db else path

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

        table_path = Database.get_table(self, table, path)
        return self.db.collection(table_path)

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

        collect = Database.get_all(self, table, path)
        return collect.all()

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

        collect = Database.get_by_key(self, table, path, key)
        # Get the entry from the collection
        return collect.fetch(int(key))

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

        collect = Database.get_by_fun(self, table, path, fun)
        # Get the entry from the collection
        return collect.filter(fun)

    def commit(self):
        """ Save all database changes to disk.
        Overrides :meth:`Database.commit`
        """
        Database.commit(self)
        self.db.commit()
        return ''

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
        # Typecast values uniformly
        def cast(value):
            # convert if numpy datatype
            if isinstance(value, np.number):
                return value.item()
            return value
        # Add entries to database
        def add_entry(entry):
            # Add a tuple entry as a dict
            if hasattr(entry, '__len__'):
                d_entry = dict(zip(t_keys, map(cast,entry)))
                self.add_entry(table, path, d_entry, update)
                return d_entry

        # Don't update if update off
        if not update:
            # Return if no more entries than exist
            existing = self.get_all(table, path)
            print len(existing), len(entries)
            if len(existing) >= len(entries):
                return []
            # Otherwise add remaining entries
            entries = entries[len(existing):]

        # Time to add entries
        start = time.time()
	count = len(entries)
        self.log('ADD', count, table)
	#####
	# Add all the entries
        #####
        dict_entries = map(add_entry, entries[:1000])

	# Log diff and total time
	diff = time.time() - start
        self.log('ADDED', count, diff)
        # Save to disk
        self.commit()
        return dict_entries

