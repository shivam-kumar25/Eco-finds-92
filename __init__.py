from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail

mail = Mail()

# Initialize extensions
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    mail = Mail(app)

    # Configuration for Flask-Mail - Replace with your Ethereal credentials
    app.config.update(
        MAIL_SERVER = 'smtp.ethereal.email',
        MAIL_PORT = 587,
        MAIL_USERNAME = 'elisa.hoeger28@ethereal.email',    # Get from Ethereal
        MAIL_PASSWORD = 'cTK6m8UsD3p8Ss1KMk',    # Get from Ethereal
        MAIL_USE_TLS = True,
        MAIL_USE_SSL = False,
        MAIL_DEBUG = True,
        MAIL_DEFAULT_SENDER = 'from@example.com'
    )


    
    # Import models to ensure they are registered with SQLAlchemy
    from models.models import User, Product, Payment, Bid, CartItem, Order, Category
    

    # Import blueprints to register them
    from routes.auth import auth 
    from routes.intro import intro
    
    from routes.user import user
    from routes.product import product
    from routes.payment import payment
    
    from routes.auction import auction
    
    
        
    
    
    
    # from routes import main
    
    # app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(intro)
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(product, url_prefix='/product')
    app.register_blueprint(payment)
    app.register_blueprint(auction, url_prefix='/auction')
    
    
    return app



