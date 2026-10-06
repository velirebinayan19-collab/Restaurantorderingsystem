from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db_connect import get_db_connection

# Define the Blueprint here
item_bp = Blueprint('item', __name__)

# 1. READ / INDEX & SEARCH
@item_bp.route('/items', methods=['GET'])
def index():
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category_id', '')
    
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    
    query = """
        SELECT items.*, categories.name AS category_name 
        FROM items 
        JOIN categories ON items.category_id = categories.id
        WHERE 1=1
    """
    params = []

    if search_query:
        query += " AND items.name LIKE ?"
        params.append(f'%{search_query}%')
    if category_filter:
        query += " AND items.category_id = ?"
        params.append(category_filter)

    query += " ORDER BY items.id DESC"
    items = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'items/index.html', 
        items=items, 
        categories=categories, 
        search_query=search_query, 
        selected_category=category_filter
    )

# 2. CREATE / ADD ITEM
@item_bp.route('/items/add', methods=['GET', 'POST'])
def add():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories").fetchall()

    if request.method == 'POST':
        name = request.form['name'].strip()
        price = request.form['price'].strip()
        description = request.form['description'].strip()
        category_id = request.form['category_id']
        is_available = int(request.form.get('is_available', 1))

        if not name or not price or not category_id:
            flash('Name, Price, and Category are required!', 'danger')
            conn.close()
            return redirect(url_for('item.add'))

        conn.execute(
            "INSERT INTO items (name, price, description, category_id, is_available) VALUES (?, ?, ?, ?, ?)",
            (name, float(price), description, category_id, is_available)
        )
        conn.commit()
        conn.close()
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('item.index'))

    conn.close()
    return render_template('items/add.html', categories=categories)

# 3. EDIT ITEM
@item_bp.route('/items/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (id,)).fetchone()
    categories = conn.execute("SELECT * FROM categories").fetchall()

    if request.method == 'POST':
        name = request.form['name'].strip()
        price = request.form['price'].strip()
        description = request.form['description'].strip()
        category_id = request.form['category_id']
        is_available = int(request.form.get('is_available', 1))

        if not name or not price or not category_id:
            flash('Name, Price, and Category are required!', 'danger')
            conn.close()
            return redirect(url_for('item.edit', id=id))

        conn.execute(
            "UPDATE items SET name = ?, price = ?, description = ?, category_id = ?, is_available = ? WHERE id = ?",
            (name, float(price), description, category_id, is_available, id)
        )
        conn.commit()
        conn.close()
        flash('Menu item updated successfully!', 'success')
        return redirect(url_for('item.index'))

    conn.close()
    return render_template('items/edit.html', item=item, categories=categories)

# 4. DELETE ITEM
@item_bp.route('/items/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM items WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Menu item deleted successfully!', 'success')
    return redirect(url_for('item.index'))