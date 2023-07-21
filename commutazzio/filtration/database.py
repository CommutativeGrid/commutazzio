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

class CLFiltrationDB:
    def __init__(self, filename:str='clf_database.db', table_name:str='filtration',create_new_db:bool=False):
        """
        initializes the database by connecting to the database file, 
        and calls create_table() method which creates a table 
        if it doesn't exist in the database.
        """
        if filename == ':memory:':
            self.conn = sqlite3.connect(':memory:')
            print('Connected to in-memory database.')
            self.create_table(table_name)
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

    def create_table(self,table_name:str):
        """
        creates a table named table_name 
        with columns for 
        id, 
        ladder_length, 
        upper, lower, 
        horizontal_parameters, 
        and info.
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

    def add_filtration(self, clfiltration):
        # Serialize the filtration object
        serialized_filtration = clfiltration.serialize()
        
        # Insert the serialized filtration into the database
        self.conn.execute(f'''INSERT INTO {self.table_name}
                            (ladder_length, upper, lower, horizontal_parameters, info)
                            VALUES (?, ?, ?, ?, ?)''',
                            (serialized_filtration['ladder_length'],
                            str(serialized_filtration['upper']),
                            str(serialized_filtration['lower']),
                            str(serialized_filtration['horizontal_parameters']),
                            str(serialized_filtration['info'])))
        # Save the changes
        self.conn.commit()
    
    def get_filtration_by_id(self, id):
        # Retrieve a row from the table by ID
        cursor = self.conn.cursor()
        cursor.execute(f'''SELECT * FROM {self.table_name} WHERE id = ?''', (id,))
        row = cursor.fetchone()
        if row:
            # If a row is found, create a new CLFiltration object and fill it with the data from the row
            cl_filtration = CLFiltration()
            cl_filtration = CLFiltration()
            cl_filtration.ladder_length = row[1]
            cl_filtration.upper = cl_filtration.incremental_filtration_creation(eval(row[2]))
            cl_filtration.lower = cl_filtration.incremental_filtration_creation(eval(row[3]))
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
        cursor = self.conn.cursor()
        cursor.execute(f'''SELECT count(*) FROM {self.table_name}''')
        return cursor.fetchone()[0]
        
    def get_all(self):
        # Retrieve all rows from the table
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


