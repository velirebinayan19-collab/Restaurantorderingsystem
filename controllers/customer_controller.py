from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db_connect import get_db_connection
import sqlite3

customer_bp = Blueprint('customer', __name__, url_prefix='/customers')

# 1. Customer List & Search (Lab 6)
@customer_bp.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '').strip()
    conn = get_db_connection()
    
    if search_query:
        query = "SELECT * FROM customers WHERE name LIKE ? OR contact LIKE ? OR email LIKE ? ORDER BY id DESC"
        param = f"%{search_query}%"
        customers = conn.execute(query, (param, param, param)).fetchall()
    else:
        customers = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
        
    conn.close()
    return render_template('customers/index.html', customers=customers, search_query=search_query)

# 2. Add Customer Form
@customer_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        contact = request.form['contact'].strip()
        email = request.form['email'].strip()

        if not name or not contact or not email:
            flash('All fields are required!', 'danger')
            return render_template('customers/add.html')

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO customers (name, contact, email) VALUES (?, ?, ?)",
                (name, contact, email)
            )
            conn.commit()
            flash('Customer registered successfully!', 'success')
            return redirect(url_for('customer.index'))
        except sqlite3.IntegrityError:
            flash('A customer with this email already exists.', 'danger')
        finally:
            conn.close()

    return render_template('customers/add.html')

# 3. Edit Customer
@customer_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    customer = conn.execute("SELECT * FROM customers WHERE id = ?", (id,)).fetchone()

    if not customer:
        conn.close()
        flash('Customer not found.', 'danger')
        return redirect(url_for('customer.index'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        contact = request.form['contact'].strip()
        email = request.form['email'].strip()

        try:
            conn.execute(
                "UPDATE customers SET name = ?, contact = ?, email = ? WHERE id = ?",
                (name, contact, email, id)
            )
            conn.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customer.index'))
        except sqlite3.IntegrityError:
            flash('This email is already in use by another customer.', 'danger')
        finally:
            conn.close()

    conn.close()
    return render_template('customers/edit.html', customer=customer)

# 4. Delete Customer
@customer_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM customers WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Customer deleted successfully.', 'info')
    return redirect(url_for('customer.index'))

# 5. Customer Profile & Order History (Lab 7)
@customer_bp.route('/profile/<int:id>', methods=['GET'])
def profile(id):
    conn = get_db_connection()
    
    # Fetch Customer Info
    customer = conn.execute("SELECT * FROM customers WHERE id = ?", (id,)).fetchone()
    
    if not customer:
        conn.close()
        flash('Customer not found.', 'danger')
        return redirect(url_for('customer.index'))

    # Fetch Customer Order History
    orders = conn.execute('''
        SELECT id, order_date, total_amount, status 
        FROM orders 
        WHERE customer_id = ? 
        ORDER BY order_date DESC
    ''', (id,)).fetchall()
    
    conn.close()
    return render_template('customers/profile.html', customer=customer, orders=orders)