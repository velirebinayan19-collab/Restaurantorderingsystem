import sqlite3

def init_db():
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    # Categories Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            is_available INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')

    # Orders Table (Lab 7)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Completed',
            FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("Database tables updated successfully!")

if __name__ == '__main__':
    init_db()