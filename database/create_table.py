import sys
import os

# Ensure Python can import db_connect when running from inside the database folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_connect import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Create orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'PENDING'
);
""")

# Create order_items table
cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL
);
""")

conn.commit()
conn.close()
print("Tables created successfully!")