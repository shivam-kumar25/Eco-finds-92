from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # Configuration for Flask-Mail with Gmail
    app.config.update(
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 587,
        MAIL_USERNAME = 'roxxkk786@gmail.com',    # Your Gmail address
        MAIL_PASSWORD = 'ziephjckiyxqnelp',      # App Password from Google Account settings
        MAIL_USE_TLS = True,
        MAIL_USE_SSL = False,
        MAIL_DEBUG = True,
        MAIL_DEFAULT_SENDER = 'roxxkk786@gmail.com'
    )
    
    # Initialize mail with app
    mail.init_app(app)
    
    # Set up logging for email diagnostics
    import logging
    app.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.logger.info("Flask-Mail configured with server: %s:%s", app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
    app.logger.info("Mail username: %s", app.config['MAIL_USERNAME'])


    
    # Import models to ensure they are registered with SQLAlchemy
    from models.models import User, Product, Payment, Bid, CartItem, Order, Category
        # Import blueprints to register them
    from routes.auth import auth 
    from routes.intro import intro
    from routes.user import user
    from routes.product import product
    from routes.payment import payment
    from routes.auction import auction
    from routes.admin import admin
    
    # Register all blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(intro)
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(product, url_prefix='/product')
    app.register_blueprint(payment)
    app.register_blueprint(auction, url_prefix='/auction')
    app.register_blueprint(admin, url_prefix='/admin')
    
    
    return app



