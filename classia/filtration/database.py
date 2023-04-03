import sqlite3
from .clfiltration import CLFiltration

class CLFiltrationDB:
    def __init__(self, filename='clf_database.db'):
        self.filename = filename
        self.conn = sqlite3.connect(self.filename)
        self.create_table()

    def create_table(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS clf_filtration
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ladder_length INT,
                            upper TEXT,
                            lower TEXT,
                            horizontal_parameters TEXT,
                            metadata JSON1)''')

    def add_filtration(self, clf_filtration):
        serialized_filtration = clf_filtration.serialize()
        self.conn.execute('''INSERT INTO clf_filtration
                            (ladder_length, upper, lower, horizontal_parameters, metadata)
                            VALUES (?, ?, ?, ?, ?)''',
                            (serialized_filtration['ladder_length'],
                            str(serialized_filtration['upper']),
                            str(serialized_filtration['lower']),
                            str(serialized_filtration['horizontal_parameters']),
                            str(serialized_filtration['metadata'])))
        self.conn.commit()
    
    def get_filtration_by_id(self, id):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM clf_filtration WHERE id = ?''', (id,))
        row = cursor.fetchone()
        if row:
            clf_filtration = CLFiltration()
            clf_filtration.ladder_length = row[1]
            clf_filtration.upper = clf_filtration.incremental_filtration_creation(eval(row[2]))
            clf_filtration.lower = clf_filtration.incremental_filtration_creation(eval(row[3]))
            clf_filtration.horizontal_parameters = eval(row[4])
            clf_filtration.metadata = eval(row[5])
            return clf_filtration
        else:
            return None
