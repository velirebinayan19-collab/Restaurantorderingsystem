from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db_connect import get_db_connection

kitchen_bp = Blueprint('kitchen', __name__, url_prefix='/kitchen')

@kitchen_bp.route('/')
def kds_dashboard():
    conn = get_db_connection()
    # Fetch active orders for kitchen display
    orders = conn.execute("""
        SELECT o.id, o.order_date, o.total_amount, o.status, c.name as customer_name
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        WHERE o.status != 'PAID'
        ORDER BY o.id ASC
    """).fetchall()
    conn.close()
    return render_template('kitchen/kds.html', orders=orders)

@kitchen_bp.route('/update/<int:order_id>', methods=['POST'])
def update_status(order_id):
    new_status = request.form.get('status')
    valid_statuses = ['PENDING', 'SENT TO KITCHEN', 'PREPARING', 'READY', 'COMPLETED', 'PAID']
    
    if new_status in valid_statuses:
        conn = get_db_connection()
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        conn.commit()
        conn.close()
        flash(f'Kitchen Order #{order_id} updated to {new_status}.', 'success')
    else:
        flash('Invalid status update.', 'danger')
        
    return redirect(url_for('kitchen.kds_dashboard'))