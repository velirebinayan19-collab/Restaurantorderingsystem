from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db_connect import get_db_connection

order_bp = Blueprint('order', __name__, url_prefix='/orders')

# Helper function to initialize session cart
def get_cart():
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']

# Root redirect /orders -> /orders/cart
@order_bp.route('/')
def index():
    return redirect(url_for('order.view_cart'))

# Lab 9 & 10: Order Cart Interface
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
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    total_quantity = sum(item['quantity'] for item in cart.values())

    return render_template(
        'orders/cart.html',
        customers=customers,
        categories=categories,
        items=items,
        selected_category_id=selected_cat_id,
        cart=cart.values(),
        subtotal=subtotal,
        total_quantity=total_quantity
    )

# Feature 1: Add Item to Cart (With Lab 10 Validation)
@order_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    item_id_raw = request.form.get('item_id')
    quantity_raw = request.form.get('quantity', 1)
    category_id = request.form.get('category_id')

    # Rule: Check if item_id and quantity are provided
    if not item_id_raw:
        flash('Validation Error: Please select a valid menu item.', 'danger')
        return redirect(url_for('order.view_cart', category_id=category_id))

    # Rule: Validate quantity numeric conversion and positive value
    try:
        quantity = int(quantity_raw)
        if quantity <= 0:
            flash('Validation Error: Quantity must be greater than zero.', 'danger')
            return redirect(url_for('order.view_cart', category_id=category_id))
    except (ValueError, TypeError):
        flash('Validation Error: Quantity must be a valid integer.', 'danger')
        return redirect(url_for('order.view_cart', category_id=category_id))

    conn = get_db_connection()
    # Rule: Invalid Menu Item & Availability Check
    item = conn.execute("SELECT id, name, price FROM items WHERE id = ?", (item_id_raw,)).fetchone()
    conn.close()

    if not item:
        flash('Validation Error: Selected menu item does not exist or is unavailable.', 'danger')
        return redirect(url_for('order.view_cart', category_id=category_id))

    cart = get_cart()
    item_id_str = str(item['id'])

    # Rule: Duplicate Item Handling (consolidate quantity)
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

# Feature 2 & 3: Update Quantity / Remove Item (With Lab 10 Validation)
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
                # Rule: Zero or Negative Quantity removes or flags error
                if new_qty > 0:
                    cart[item_id_str]['quantity'] = new_qty
                    flash('Cart updated successfully.', 'success')
                else:
                    del cart[item_id_str]
                    flash('Item removed because quantity was set to zero or negative.', 'info')
            except (ValueError, TypeError):
                flash('Validation Error: Invalid quantity entered.', 'danger')
        
        session.modified = True

    return redirect(url_for('order.view_cart'))

# Feature 5: Clear Cart
@order_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    flash('Cart cleared.', 'info')
    return redirect(url_for('order.view_cart'))

# Finalize Order (With Lab 10 Server-Side Checkout Validation)
@order_bp.route('/cart/checkout', methods=['POST'])
def checkout():
    customer_id = request.form.get('customer_id')
    cart = get_cart()

    # Rule 1: Empty Order Validation
    if not cart or len(cart) == 0:
        flash('Validation Error: Cannot place an empty order. Please add items to your cart.', 'danger')
        return redirect(url_for('order.view_cart'))

    # Rule 2: Invalid Customer Validation
    if not customer_id:
        flash('Validation Error: Please select a valid customer.', 'danger')
        return redirect(url_for('order.view_cart'))

    conn = get_db_connection()
    try:
        customer = conn.execute("SELECT id FROM customers WHERE id = ?", (customer_id,)).fetchone()
        if not customer:
            flash('Validation Error: Selected customer does not exist in the database.', 'danger')
            return redirect(url_for('order.view_cart'))

        # Rule 3 & 4: Validate items, prices, and non-zero positive quantities before checkout
        validated_items = []
        for item_id_str, cart_item in list(cart.items()):
            db_item = conn.execute("SELECT id, price FROM items WHERE id = ?", (cart_item['id'],)).fetchone()
            
            # Invalid item or item removed from database
            if not db_item:
                flash(f'Validation Error: Item "{cart_item["name"]}" is no longer available.', 'danger')
                del cart[item_id_str]
                session.modified = True
                return redirect(url_for('order.view_cart'))

            # Check quantity sanity
            if cart_item['quantity'] <= 0:
                flash(f'Validation Error: Invalid quantity for item "{cart_item["name"]}".', 'danger')
                return redirect(url_for('order.view_cart'))

            validated_items.append({
                'id': db_item['id'],
                'price': float(db_item['price']),
                'quantity': cart_item['quantity']
            })

        subtotal = sum(i['price'] * i['quantity'] for i in validated_items)

        # Process valid order into database
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (?, datetime('now'), ?, 'Pending')",
            (customer_id, subtotal)
        )
        order_id = cursor.lastrowid

        # Insert item details into order_items table if applicable
        for item in validated_items:
            cursor.execute(
                "INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (?, ?, ?, ?)",
                (order_id, item['id'], item['quantity'], item['price'])
            )

        # Clear cart on successful transaction
        session.pop('cart', None)
        conn.commit()
        flash(f'Order #{order_id} validated and placed successfully! Subtotal: ₱{subtotal:.2f}', 'success')
        return redirect(url_for('customer.profile', id=customer_id))

    except Exception as e:
        conn.rollback()
        flash(f'An unexpected database error occurred: {str(e)}', 'danger')
        return redirect(url_for('order.view_cart'))
    finally:
        conn.close()