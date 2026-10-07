import sqlite3

def init_db():
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Categories Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')

    # 2. Items Table
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

    # 3. Re-create Customers Table with correct schema
    # Drop old table if 'contact' column exists to resolve NOT NULL constraint error
    cursor.execute("PRAGMA table_info(customers)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'contact' in columns:
        cursor.execute("DROP TABLE customers;")
        print("Dropped outdated customers table containing 'contact' constraint.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )
    ''')

    # 4. Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
        )
    ''')

    # 5. Order Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database schema successfully fixed and updated!")

if __name__ == '__main__':
    init_db()