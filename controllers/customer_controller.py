from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db_connect import get_db_connection
import re

customer_bp = Blueprint('customer', __name__, url_prefix='/customers')

# Helper validation functions
def is_valid_email(email):
    if not email:
        return True # Optional field
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone):
    if not phone:
        return True # Optional field
    pattern = r'^\+?[0-9]{7,15}$'
    return bool(re.match(pattern, phone))

# 1. List Customers
@customer_bp.route('/')
def index():
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('customers/index.html', customers=customers)

# 2. Add Customer
@customer_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        if not name:
            flash('Customer name is required.', 'danger')
            return redirect(url_for('customer.add'))

        if email and not is_valid_email(email):
            flash('Please enter a valid email address (e.g., name@example.com).', 'danger')
            return redirect(url_for('customer.add'))

        if phone and not is_valid_phone(phone):
            flash('Please enter a valid phone number (7 to 15 digits).', 'danger')
            return redirect(url_for('customer.add'))

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
                (name, email, phone)
            )
            conn.commit()
            conn.close()

            flash('Customer added successfully!', 'success')
            return redirect(url_for('customer.index'))
        except Exception as e:
            flash(f'Database error: {str(e)}', 'danger')
            return redirect(url_for('customer.add'))

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
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        if not name:
            conn.close()
            flash('Customer name is required.', 'danger')
            return redirect(url_for('customer.edit', id=id))

        if email and not is_valid_email(email):
            conn.close()
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('customer.edit', id=id))

        if phone and not is_valid_phone(phone):
            conn.close()
            flash('Please enter a valid phone number (7 to 15 digits).', 'danger')
            return redirect(url_for('customer.edit', id=id))

        try:
            conn.execute(
                "UPDATE customers SET name = ?, email = ?, phone = ? WHERE id = ?",
                (name, email, phone, id)
            )
            conn.commit()
            conn.close()

            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customer.index'))
        except Exception as e:
            conn.close()
            flash(f'Database error: {str(e)}', 'danger')
            return redirect(url_for('customer.edit', id=id))

    conn.close()
    return render_template('customers/edit.html', customer=customer)

# 4. Delete Customer
@customer_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM customers WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        flash('Customer deleted successfully.', 'info')
    except Exception as e:
        flash(f'Error deleting customer: {str(e)}', 'danger')
    return redirect(url_for('customer.index'))

# 5. Customer Profile & Order History
@customer_bp.route('/<int:id>/profile', methods=['GET'])
def profile(id):
    conn = get_db_connection()
    
    customer = conn.execute("SELECT * FROM customers WHERE id = ?", (id,)).fetchone()
    if not customer:
        conn.close()
        flash('Customer not found.', 'danger')
        return redirect(url_for('customer.index'))

    orders = conn.execute("""
        SELECT id, order_date, total_amount, status
        FROM orders
        WHERE customer_id = ?
        ORDER BY id DESC
    """, (id,)).fetchall()

    conn.close()
    return render_template('customers/profile.html', customer=customer, orders=orders)