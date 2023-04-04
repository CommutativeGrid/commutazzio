import sqlite3
from .clfiltration import CLFiltration
import json
"""
creating and managing a SQLite database 
for storing and retrieving instances of CLFiltration.
"""

class CLFiltrationDB:
    def __init__(self, filename='clf_database.db'):
        """
         initializes the database by connecting to the database file, 
         and calls create_table() method which creates a table 
         if it doesn't exist in the database.
         """
        self.filename = filename
        self.conn = sqlite3.connect(self.filename)
        self.create_table()

    def create_table(self):
        """
        creates a table named clf_filtration 
        with columns for 
        id, 
        ladder_length, 
        upper, lower, 
        horizontal_parameters, 
        and metadata.
        """
        self.conn.execute('''CREATE TABLE IF NOT EXISTS clf_filtration
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ladder_length INT,
                            upper TEXT,
                            lower TEXT,
                            horizontal_parameters TEXT,
                            metadata JSON1)''')

    def add_filtration(self, clf_filtration):
        # Serialize the filtration object
        serialized_filtration = clf_filtration.serialize()
        
        # Insert the serialized filtration into the database
        self.conn.execute('''INSERT INTO clf_filtration
                            (ladder_length, upper, lower, horizontal_parameters, metadata)
                            VALUES (?, ?, ?, ?, ?)''',
                            (serialized_filtration['ladder_length'],
                            str(serialized_filtration['upper']),
                            str(serialized_filtration['lower']),
                            str(serialized_filtration['horizontal_parameters']),
                            json.dumps(serialized_filtration['metadata'])))
        # Save the changes
        self.conn.commit()
    
    def get_filtration_by_id(self, id):
        # Retrieve a row from the table by ID
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM clf_filtration WHERE id = ?''', (id,))
        row = cursor.fetchone()
        if row:
            # If a row is found, create a new CLFiltration object and fill it with the data from the row
            clf_filtration = CLFiltration()
            clf_filtration = CLFiltration()
            clf_filtration.ladder_length = row[1]
            clf_filtration.upper = clf_filtration.incremental_filtration_creation(eval(row[2]))
            clf_filtration.lower = clf_filtration.incremental_filtration_creation(eval(row[3]))
            clf_filtration.horizontal_parameters = eval(row[4])
            clf_filtration.metadata = json.loads(row[5])
            return clf_filtration
        else:
            return None
        
    def read_all(self):
        # Retrieve all rows from the table
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM clf_filtration''')
        rows = cursor.fetchall()
        filtrations=[]
        # Create a new CLFiltration object for each row and add it to a list
        for row in rows:
            filtrations.append(self.get_filtration_by_id(row[0]))
        return filtrations


