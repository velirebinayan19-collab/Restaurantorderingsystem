from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db_connect import get_db_connection

category_bp = Blueprint('category', __name__)

# 1. READ / INDEX & SEARCH
@category_bp.route('/categories', methods=['GET'])
def index():
    search_query = request.args.get('search', '').strip()
    conn = get_db_connection()
    if search_query:
        categories = conn.execute("SELECT * FROM categories WHERE name LIKE ?", ('%' + search_query + '%',)).fetchall()
    else:
        categories = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return render_template('categories/index.html', categories=categories, search_query=search_query)

# 2. CREATE / ADD
@category_bp.route('/categories/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Category name cannot be empty!', 'danger')
            return redirect(url_for('category.add'))
        
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('category.index'))
        except Exception as e:
            flash(f'Error: Category might already exist. ({e})', 'danger')
        finally:
            conn.close()

    return render_template('categories/add.html')

# 3. EDIT / UPDATE
@category_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    category = conn.execute("SELECT * FROM categories WHERE id = ?", (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Category name cannot be empty!', 'danger')
            return redirect(url_for('category.edit', id=id))

        conn.execute("UPDATE categories SET name = ? WHERE id = ?", (name, id))
        conn.commit()
        conn.close()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('category.index'))

    conn.close()
    return render_template('categories/edit.html', category=category)

# 4. DELETE
@category_bp.route('/categories/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM categories WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('category.index'))