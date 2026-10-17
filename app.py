from flask import Flask, render_template
from pyngrok import ngrok

from controllers.category_controller import category_bp
from controllers.item_controller import item_bp
from controllers.customer_controller import customer_bp
from controllers.order_controller import order_bp
from controllers.kitchen_controller import kitchen_bp

app = Flask(__name__, template_folder='views', static_folder='assets')
app.secret_key = 'super_secret_key'

app.register_blueprint(category_bp)
app.register_blueprint(item_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(order_bp)
app.register_blueprint(kitchen_bp)

@app.route('/')
def home():
    return render_template('dashboard.html')

# Authenticate ngrok
ngrok.set_auth_token("3KOCnqRvU1w0rqhSl3CcvWPKQS6_6Hp4mSMQ1GdZVmzdB8Mfw")

# Connect using your static domain with pooling enabled to bypass the 502 online lock
tunnel = ngrok.connect(5000, domain="motor-cornball-doorstep.ngrok-free.dev", pooling_enabled=True)
print(f"\n * STATIC NGROK URL: {tunnel.public_url}\n")

if __name__ == '__main__':
    app.run(port=5000, debug=True)