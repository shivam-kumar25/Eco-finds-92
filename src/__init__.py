from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from src.config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from src.models.user import User
    from src.models.product import Product
    from src.models.category import Category
    from src.models.cart import CartItem
    from src.models.order import Order, OrderItem
    
    # Import and register blueprints
    from src.routes.main import main
    from src.routes.auth import auth
    from src.routes.products import products
    from src.routes.cart import cart
    from src.routes.orders import orders
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(products, url_prefix='/products')
    app.register_blueprint(cart, url_prefix='/cart')
    app.register_blueprint(orders, url_prefix='/orders')
    
    return app
