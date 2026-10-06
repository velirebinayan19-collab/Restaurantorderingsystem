import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database/restaurant.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

if __name__ == "__main__":
    try:
        conn = get_db_connection()
        print("Database connected successfully.")
        conn.close()
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")