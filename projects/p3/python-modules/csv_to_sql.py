"""Import the content of the .csv files into a SQL database.

Note: Use Python 3 to run this script.

* Module 5 of 6

References
-------------------------------------------------------------------------------
[1] 'Project: Wrangle OpenStreetMap Data', Data Wrangling Course, Udacity Data
     Analyst Nanodegree
[2] https://docs.python.org/3/library/sqlite3.html
[3] https://stackoverflow.com/questions/15513854/sqlite3-warning-you-can-only-
    execute-one-statement-at-a-time
[4] https://stackoverflow.com/questions/2887878/importing-a-csv-file-into-a-
    sqlite3-database-table-using-python
[5] https://en.wikipedia.org/wiki/Prepared_statement

2017 - Federico Maria Massari / federico.massari@bocconialumni.it
"""

import sqlite3
import csv
import pandas as pd

# Store the data in the 'milan_italy.db' file
sqlite_database = 'milan_italy.db'

# Create a Connection object that represents the database [1], [2]
conn = sqlite3.connect(sqlite_database)

# Create a Cursor object, which runs queries and fetches results
c = conn.cursor()

# Open and read the data wrangling schema to insert into the SQL database
dw_schema = 'data_wrangling_schema.sql'
query = open(dw_schema, 'r').read()

"""Import data wrangling schema into the open database. Using .execute() will
raise 'Warning: You can only execute one statement at a time.' .executescript()
allows instead to execute multiple SQL statements with one single call [3].
"""
c.executescript(query)

"""The database now contains five empty tables accessible via Terminal or
Command Prompt:
$ sqlite3 milan_italy.db
sqlite> .tables                 <- For a list of tables in the database
sqlite> .schema <tablename>     <- For the schema of individual tables
"""

# Fill database tables with the content of the csv files output of data.py [4]
def csv_to_sql(csv_file, directory=''):
    """Import the content of a csv file into a SQL database table, whose name
    is specified by the csv filename (without extension).

    Arguments:
        csv_file -- str. The full name of the csv file, e.g., 'nodes.csv';

    Keyword arguments:
        directory -- str. The folder containing the csv file. Must include
            forward slash at the end, e.g. './' (default '').

    Returns:
        Updated SQL tables, with entries from the supplied csv files.
    """
    file_path = directory + csv_file

    # Read header from csv file and store it in a list
    fields = list(pd.read_csv(file_path, nrows=0))

    with open(file_path, 'r') as f:
        dr = csv.DictReader(f)

        # For 'nodes', the inner list comprehension gives i['id'], i['lat'], ...
        to_db = [[i[field] for field in fields] for i in dr]

    """Use .executemany() to execute an SQL command against all parameter
    sequences or mappings found in the sequence 'to_db' [2].

    The syntax for executemany() [2] is executemany(SQL, [parameters]), where
    SQL has three {} spots to fill (using .format()): 1. table name; 2. value
    fields; 3. the number of question marks for the prepared statement [5].

    1. Table name: split input csv file on extension dot and take the left
                   element, e.g. 'nodes.csv' -> 'nodes';
    2. Value fields: join all fields in the 'fields' list with a comma and a
                     blank space, e.g. ['id', 'lat', 'lon', 'user', ...] ->
                     id, lat, lon, user, ...
    3. No. question marks: concatenate n question marks, with n the length of
                           the list 'fields', followed by a comma and a blank
                           space; then strip the last comma and blank space,
                           e.g. len(fields) = 8 -> '?, '*8 -> '?, ?, ?, ...,
                           ?, ' -> (rstrip) '?, ...., ?'.
    """
    c.executemany('INSERT INTO {} ({}) VALUES ({});'\
                .format(csv_file.split('.')[0], ', '.join(fields), \
                        ('?, ' * len(fields)).rstrip(', ')), to_db)

# Store filenames and lists of fields into separate lists, for neater code
directory = './csv/'
files = ['nodes.csv', 'nodes_tags.csv', 'ways.csv', 'ways_nodes.csv', \
            'ways_tags.csv', 'municipalities.csv']

# Insert csv content into SQL tables
[csv_to_sql(files[i], directory) for i in range(len(files))]

# Commit all changes and close the Connection object (i.e. the database)
conn.commit()
conn.close()
