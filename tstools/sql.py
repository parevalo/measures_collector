# Functions for interacting with SQL-lite database

import os
import sqlite3

# Check if database exist, and make if not
def make_db(dbPath, command):

    if not os.path.isfile(dbPath):
        conn = sqlite3.connect(dbPath)
        c = conn.cursor()
        c.execute(command)
        print('Database created')
    else:
        conn = sqlite3.connect(dbPath)

    return conn
