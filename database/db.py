# Database connection - every entity class gets its connection from here

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "archss.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def getConnection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row     # lets us do row["profileName"]
    return conn


def initDatabase():
    # creates the tables (only if they don't exist yet)
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn = getConnection()
        conn.executescript(f.read())
        conn.commit()
        conn.close()
