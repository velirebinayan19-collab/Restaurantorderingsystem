from flask import Flask, render_template

from controllers.category_controller import category_bp
from controllers.item_controller import item_bp
from controllers.customer_controller import customer_bp
from controllers.order_controller import order_bp
from controllers.kitchen_controller import kitchen_bp

# Ensure template_folder matches your project structure ('views' or 'templates')
app = Flask(__name__, template_folder='views', static_folder='assets')
app.secret_key = 'super_secret_key'  # Required for Flask session cart

app.register_blueprint(category_bp)
app.register_blueprint(item_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(order_bp)
app.register_blueprint(kitchen_bp)

@app.route('/')
def home():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)