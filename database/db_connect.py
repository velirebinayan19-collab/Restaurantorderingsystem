import sqlite3
import os

# Get absolute path to database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'restaurant.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

if __name__ == "__main__":
    conn = get_db_connection()
    print("Database connected successfully.")
    conn.close()