import sqlite3

def seed_db():
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Categories
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ('Appetizers',),
            ('Main Course',),
            ('Desserts',),
            ('Beverages',)
        ]
        cursor.executemany("INSERT INTO categories (name) VALUES (?)", categories)

    # 2. Menu Items
    cursor.execute("SELECT id, name FROM categories")
    category_map = {name: cat_id for cat_id, name in cursor.fetchall()}

    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0 and category_map:
        menu_items = [
            (category_map.get('Appetizers', 1), 'Caesar Salad', 8.99, 'Fresh romaine lettuce with Caesar dressing'),
            (category_map.get('Main Course', 2), 'Grilled Salmon', 24.99, 'Fresh Atlantic salmon grilled to perfection'),
            (category_map.get('Desserts', 3), 'Tiramisu', 7.99, 'Classic Italian dessert with coffee and mascarpone'),
            (category_map.get('Beverages', 4), 'Iced Tea', 3.99, 'Refreshing brewed tea served over ice')
        ]
        cursor.executemany("INSERT INTO items (category_id, name, price, description) VALUES (?, ?, ?, ?)", menu_items)

    # 3. Customer
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO customers (name, phone, email)
            VALUES ('Velire Binayan', '09123456789', 'velire@email.com')
        ''')

    conn.commit()
    conn.close()
    print("Database seeded with Categories, Items, and Customers successfully!")

if __name__ == '__main__':
    seed_db()