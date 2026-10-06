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
            INSERT INTO customers (name, contact, email)
            VALUES ('Velire Binayan', '09123456789', 'velire@email.com')
        ''')

    # 4. Orders
    cursor.execute("SELECT id FROM customers LIMIT 1")
    customer = cursor.fetchone()

    if customer:
        customer_id = customer[0]
        cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ?", (customer_id,))
        if cursor.fetchone()[0] == 0:
            sample_orders = [
                (customer_id, '2026-10-01 12:30:00', 37.97, 'Completed'),
                (customer_id, '2026-10-05 18:45:00', 19.98, 'Pending'),
                (customer_id, '2026-10-06 11:15:00', 45.50, 'Completed')
            ]
            cursor.executemany('''
                INSERT INTO orders (customer_id, order_date, total_amount, status)
                VALUES (?, ?, ?, ?)
            ''', sample_orders)

    conn.commit()
    conn.close()
    print("Database seeded with Categories, Items, Customers, and Orders successfully!")

if __name__ == '__main__':
    seed_db()