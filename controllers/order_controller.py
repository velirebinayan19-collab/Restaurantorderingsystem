from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db_connect import get_db_connection

order_bp = Blueprint('order', __name__, url_prefix='/orders')

def get_cart():
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']

@order_bp.route('/')
def index():
    return redirect(url_for('order.view_cart'))

# View Cart & Bill Breakdown (Labs 11, 15 & 16 Combined)
@order_bp.route('/cart', methods=['GET'])
def view_cart():
    conn = get_db_connection()
    customers = conn.execute("SELECT id, name FROM customers ORDER BY name ASC").fetchall()
    categories = conn.execute("SELECT MIN(id) as id, name FROM categories GROUP BY name ORDER BY name ASC").fetchall()
    
    selected_cat_id = request.args.get('category_id', type=int)
    items = []
    if selected_cat_id:
        items = conn.execute("SELECT id, name, price FROM items WHERE category_id = ?", (selected_cat_id,)).fetchall()

    conn.close()

    cart = get_cart()
    
    # Lab 15: Subtotal and Total Quantity Calculations
    subtotal = sum(float(item['price']) * int(item['quantity']) for item in cart.values())
    total_quantity = sum(int(item['quantity']) for item in cart.values())

    # Lab 16: Discounts & Charges Calculations
    discount_percent = float(request.args.get('discount', 10.0))  # Default 10% discount
    discount_amount = subtotal * (discount_percent / 100.0)
    other_charges = 0.00
    
    # Formula: Final Total = Subtotal - Discount + Other Charges
    final_total = subtotal - discount_amount + other_charges

    return render_template(
        'orders/cart.html',
        customers=customers,
        categories=categories,
        items=items,
        selected_category_id=selected_cat_id,
        cart=cart.values(),
        subtotal=subtotal,
        total_quantity=total_quantity,
        discount_percent=discount_percent,
        discount_amount=discount_amount,
        other_charges=other_charges,
        final_total=final_total
    )

# Add Item to Cart
@order_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    item_id_raw = request.form.get('item_id')
    quantity_raw = request.form.get('quantity', 1)
    category_id = request.form.get('category_id')

    if not item_id_raw:
        flash('Validation Error: Please select a valid menu item.', 'danger')
        return redirect(url_for('order.view_cart', category_id=category_id))

    try:
        quantity = int(quantity_raw)
        if quantity <= 0:
            flash('Validation Error: Quantity must be greater than zero.', 'danger')
            return redirect(url_for('order.view_cart', category_id=category_id))
    except (ValueError, TypeError):
        flash('Validation Error: Quantity must be a valid integer.', 'danger')
        return redirect(url_for('order.view_cart', category_id=category_id))

    conn = get_db_connection()
    item = conn.execute("SELECT id, name, price FROM items WHERE id = ?", (item_id_raw,)).fetchone()
    conn.close()

    if not item:
        flash('Validation Error: Selected menu item does not exist.', 'danger')
        return redirect(url_for('order.view_cart', category_id=category_id))

    cart = get_cart()
    item_id_str = str(item['id'])

    if item_id_str in cart:
        cart[item_id_str]['quantity'] += quantity
    else:
        cart[item_id_str] = {
            'id': item['id'],
            'name': item['name'],
            'price': float(item['price']),
            'quantity': quantity
        }
    
    session.modified = True
    flash(f'Added {item["name"]} (x{quantity}) to cart.', 'success')
    return redirect(url_for('order.view_cart', category_id=category_id))

# Cart Management Actions
@order_bp.route('/cart/update', methods=['POST'])
def update_cart():
    item_id_str = str(request.form.get('item_id'))
    action = request.form.get('action')
    cart = get_cart()

    if item_id_str in cart:
        if action == 'remove':
            del cart[item_id_str]
            flash('Item removed from cart.', 'info')
        elif action == 'update':
            try:
                new_qty = int(request.form.get('quantity', 1))
                if new_qty > 0:
                    cart[item_id_str]['quantity'] = new_qty
                    flash('Cart updated.', 'success')
                else:
                    del cart[item_id_str]
                    flash('Item removed from cart.', 'info')
            except (ValueError, TypeError):
                flash('Invalid quantity.', 'danger')
        session.modified = True

    return redirect(url_for('order.view_cart'))

@order_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    flash('Cart cleared.', 'info')
    return redirect(url_for('order.view_cart'))

# Checkout & Order Total Computation (Labs 11, 15 & 16)
@order_bp.route('/cart/checkout', methods=['POST'])
def checkout():
    customer_id = request.form.get('customer_id')
    cart = get_cart()

    if not cart or len(cart) == 0:
        flash('Cannot place an empty order.', 'danger')
        return redirect(url_for('order.view_cart'))

    if not customer_id:
        flash('Please select a valid customer.', 'danger')
        return redirect(url_for('order.view_cart'))

    conn = get_db_connection()
    try:
        customer = conn.execute("SELECT id FROM customers WHERE id = ?", (customer_id,)).fetchone()
        if not customer:
            flash('Selected customer does not exist.', 'danger')
            return redirect(url_for('order.view_cart'))

        validated_items = []
        for item_id_str, cart_item in list(cart.items()):
            db_item = conn.execute("SELECT id, price FROM items WHERE id = ?", (cart_item['id'],)).fetchone()
            if not db_item:
                flash(f'Item "{cart_item["name"]}" is no longer available.', 'danger')
                return redirect(url_for('order.view_cart'))

            validated_items.append({
                'id': db_item['id'],
                'price': float(db_item['price']),
                'quantity': int(cart_item['quantity'])
            })

        # --- LAB 15: Subtotal Computation ---
        subtotal = sum(i['price'] * i['quantity'] for i in validated_items)

        # --- LAB 16: Discount and Additional Charges Computation ---
        discount_rate = float(request.form.get('discount_rate', 0.10))  # 10% discount rate
        discount_amount = subtotal * discount_rate
        other_charges = 0.00
        
        # Final Total = Subtotal - Discount + Other Charges
        final_total = subtotal - discount_amount + other_charges

        initial_status = 'PENDING'

        cursor = conn.cursor()
        # Save the discounted final_total into total_amount
        cursor.execute(
            """INSERT INTO orders (customer_id, order_date, total_amount, status) 
               VALUES (?, datetime('now', 'localtime'), ?, ?)""",
            (customer_id, final_total, initial_status)
        )
        order_id = cursor.lastrowid

        for item in validated_items:
            cursor.execute(
                """INSERT INTO order_items (order_id, item_id, quantity, price) 
                   VALUES (?, ?, ?, ?)""",
                (order_id, item['id'], item['quantity'], item['price'])
            )

        conn.commit()
        session.pop('cart', None)
        flash(f'Order #{order_id} placed successfully! Subtotal: ₱{subtotal:.2f}, Discount: -₱{discount_amount:.2f}, Final Total: ₱{final_total:.2f}', 'success')
        return redirect(url_for('order.track_orders'))

    except Exception as e:
        conn.rollback()
        flash(f'Database error placing order: {str(e)}', 'danger')
        return redirect(url_for('order.view_cart'))
    finally:
        conn.close()

# Order Tracker
@order_bp.route('/track', methods=['GET'])
def track_orders():
    conn = get_db_connection()
    orders = conn.execute("""
        SELECT o.id, o.order_date, o.total_amount, o.status, c.name as customer_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        ORDER BY o.id DESC
    """).fetchall()
    conn.close()
    return render_template('orders/track.html', orders=orders)

# Status Update Handler (Used by Order Tracker & KDS)
@order_bp.route('/update-status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    new_status = request.form.get('status')
    valid_statuses = ['PENDING', 'SENT TO KITCHEN', 'PREPARING', 'READY', 'COMPLETED', 'PAID']
    
    if new_status in valid_statuses:
        conn = get_db_connection()
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        conn.commit()
        conn.close()
        flash(f'Order #{order_id} status updated to: {new_status}', 'info')
    else:
        flash('Invalid status selected.', 'danger')
        
    return redirect(request.referrer or url_for('order.track_orders'))
# Lab 17: Payment Processing Route
@order_bp.route('/pay/<int:order_id>', methods=['GET', 'POST'])
def process_payment(order_id):
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    
    if not order:
        conn.close()
        flash('Order not found.', 'danger')
        return redirect(url_for('order.track_orders'))
        
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        try:
            amount_paid = float(request.form.get('amount_paid', 0))
        except ValueError:
            amount_paid = 0.0
            
        amount_due = float(order['total_amount'])
        
        if amount_paid < amount_due:
            flash(f'Insufficient payment. Amount due is ₱{amount_due:.2f}', 'danger')
            conn.close()
            return redirect(url_for('order.process_payment', order_id=order_id))
            
        change = amount_paid - amount_due
        balance = 0.0  # Fully paid
        
        # Update order status to PAID
        conn.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            ('PAID', order_id)
        )
        conn.commit()
        conn.close()
        
        flash(f'Payment successful! Method: {payment_method} | Amount Due: ₱{amount_due:.2f} | Paid: ₱{amount_paid:.2f} | Change: ₱{change:.2f}', 'success')
        return redirect(url_for('order.track_orders'))
        
    conn.close()
    return render_template('orders/pay.html', order=order)
# Kitchen Display System (KDS) Route
@order_bp.route('/kds', methods=['GET'])
def kitchen_display():
    conn = get_db_connection()
    
    orders_rows = conn.execute("""
        SELECT o.id, o.order_date, o.status, c.name as customer_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.status IN ('PENDING', 'SENT TO KITCHEN', 'PREPARING', 'READY')
        ORDER BY o.id ASC
    """).fetchall()

    kds_orders = []
    for order in orders_rows:
        order_items = conn.execute("""
            SELECT oi.quantity, i.name as item_name
            FROM order_items oi
            JOIN items i ON oi.item_id = i.id
            WHERE oi.order_id = ?
        """, (order['id'],)).fetchall()

        kds_orders.append({
            'id': order['id'],
            'customer_name': order['customer_name'],
            'order_date': order['order_date'],
            'status': order['status'],
            'order_items': order_items
        })

    conn.close()
    return render_template('orders/kds.html', orders=kds_orders)