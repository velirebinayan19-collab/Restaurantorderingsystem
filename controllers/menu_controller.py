from flask import Blueprint, render_template, request
from database.db_connect import get_db_connection

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/menu', methods=['GET'])
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

    query += " ORDER BY items.is_available DESC, items.name ASC"
    items = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'menu/index.html',
        items=items,
        categories=categories,
        search_query=search_query,
        selected_category=category_filter
    )