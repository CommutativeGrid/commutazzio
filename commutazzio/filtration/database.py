import sqlite3
from .clfiltration import CLFiltration
"""
creating and managing a SQLite database 
for storing and retrieving instances of CLFiltration.
"""
from orjson import loads
from ast import literal_eval
import os
from functools import cache
import gc

class CLFiltrationDB:
    """
    A class for creating and managing a SQLite database to store and retrieve 
    instances of CLFiltration.
    
    Parameters
    ----------
    filename : str, optional
        The name of the database file to connect to. If ':memory:', creates a 
        temporary in-memory database. Defaults to 'clf_database.db'.
    table_name : str, optional
        The name of the table within the database to create or use. 
        Defaults to 'filtration'.
    create_new_db : bool, optional
        If True, creates a new database file if one does not exist. Raises an 
        exception if the file already exists. Defaults to False.
    
    Attributes
    ----------
    conn : sqlite3.Connection
        The connection object to the database.
    filename : str
        The name of the database file.
    table_name : str
        The name of the table used for storing filtration data.
    
    Raises
    ------
    Exception
        If `create_new_db` is True and the database file already exists, or if
        the database file does not exist when `create_new_db` is False.
        
    """
    def __init__(self, filename:str='clf_database.db', table_name:str='filtration',create_new_db:bool=False):
        if filename == ':memory:':
            self.conn = sqlite3.connect(':memory:')
            print('Connected to in-memory database.')
            self.create_table(table_name)
            self.table_name = table_name
            return
        # add .db if no .db in filename
        if '.db' not in filename:
            filename = filename + '.db'
        self.filename = filename
        self.table_name = table_name
        #check whether self.filename exists
        if create_new_db:
            if os.path.exists(self.filename):
                raise Exception(f"{self.filename} already exists.")
            else:
                print(f"Creating {self.filename} database.")
                self.conn = sqlite3.connect(self.filename)
                self.create_table(self.table_name)
        else:
            if os.path.exists(self.filename):
                self.conn = sqlite3.connect(self.filename)
                print(f"Connected to {self.filename} database.")
            else:
                raise Exception(f"{self.filename} does not exist.")
            
    def reset_table_name_for_legacy(self):
        """
        Resets the table name to the first table found in the database.
        
        This method is intended for legacy support and updates the instance's
        table name attribute to match the first table name found in the
        database schema.
        """
        c=self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        self.table_name = tables[0][0]
            
    def close(self):
        """
        Closes the database connection.
        """
        self.conn.close()
        print(f"Closed {self.filename} database.")

    def create_table(self,table_name:str):
        """
        Creates a table in the database with a specified name if it doesn't exist.
        
        Parameters
        ----------
        table_name : str
            The name of the table to be created.
        
        Notes
        -----
        The table will have columns for id (primary key), ladder_length, upper, 
        lower, horizontal_parameters, and info (stored in JSON format).
        """
        # print information if find the table already exists
        assert isinstance(table_name,str)
        cursor = self.conn.cursor()
        cursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}' ''')
        if cursor.fetchone()[0] == 1:
            print('Table already exists.')
        else:
            print('creating table...')
            self.conn.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                ladder_length INT,
                                upper TEXT,
                                lower TEXT,
                                horizontal_parameters TEXT,
                                info JSON1)''')

    def add_filtration(self, clfiltration:CLFiltration, store_minimal_data:bool=False):
        """
        Adds a CLFiltration instance to the database.
        
        Parameters
        ----------
        clfiltration : CLFiltration
            The CLFiltration instance to store in the database.
        store_minimal_data : bool, optional
            If True, only stores the ladder_length and info of the CLFiltration 
            instance. Defaults to False.
        """
        serialized_filtration = clfiltration.serialize() # Serialize the filtration object
    
        if store_minimal_data:
            self.conn.execute(f'''INSERT INTO {self.table_name} 
                              (ladder_length, info) VALUES (?, ?)''',
                          (serialized_filtration['ladder_length'],
                           str(serialized_filtration['info'])))
        else:
            # Insert the serialized filtration into the database
            self.conn.execute(f'''INSERT INTO {self.table_name}
                                (ladder_length, upper, lower, horizontal_parameters, info)
                                VALUES (?, ?, ?, ?, ?)''',
                                (serialized_filtration['ladder_length'],
                                str(serialized_filtration['upper']),
                                str(serialized_filtration['lower']),
                                str(serialized_filtration['horizontal_parameters']),
                                str(serialized_filtration['info'])))
        del serialized_filtration
        gc.collect()
        # Save the changes
        self.conn.commit()
    
    def get_filtration_by_id(self, id:int):
        """
        Retrieves a CLFiltration instance from the database by its ID.
        
        Parameters
        ----------
        id : int
            The ID of the CLFiltration instance to retrieve.
        
        Returns
        -------
        CLFiltration or None
            The CLFiltration instance corresponding to the given ID, or None if 
            no instance is found.
        """
        cursor = self.conn.cursor()
        cursor.execute(f'''SELECT * FROM {self.table_name} WHERE id = ?''', (id,))
        row = cursor.fetchone()
        if row:
            # If a row is found, create a new CLFiltration object and fill it with the data from the row
            cl_filtration = CLFiltration()
            cl_filtration.ladder_length = row[1]
            if row[2] is not None:
                cl_filtration.upper = cl_filtration.incremental_filtration_creation(eval(row[2]))
            if row[3] is not None:
                cl_filtration.lower = cl_filtration.incremental_filtration_creation(eval(row[3]))
            if row[4] is not None:
                try:
                    cl_filtration.horizontal_parameters = loads(literal_eval(row[4]))
                except Exception as e:
                    print(e)
            cl_filtration.info = loads(literal_eval(row[5]))
            return cl_filtration
        else:
            return None
    
    @cache
    def __len__(self):
        """
        Returns the number of filtration records in the table.
        
        Returns
        -------
        int
            The number of records in the database table.
        """
        cursor = self.conn.cursor()
        cursor.execute(f'''SELECT count(*) FROM {self.table_name}''')
        return cursor.fetchone()[0]
        
    def get_all(self):
        """
        Retrieves all CLFiltration instances from the database.
        
        Returns
        -------
        generator of CLFiltration
            A generator that yields CLFiltration instances for each record in 
            the database table.
        """
        cursor = self.conn.cursor()
        cursor.execute(f'''SELECT * FROM {self.table_name}''')
        rows = cursor.fetchall()
        # return a generator
        print(f"found {len(rows)} records")
        return (self.get_filtration_by_id(row[0]) for row in rows)
        # filtrations=[]
        # # Create a new CLFiltration object for each row and add it to a list
        # for row in rows:
        #     filtrations.append(self.get_filtration_by_id(row[0]))
        # return filtrations


