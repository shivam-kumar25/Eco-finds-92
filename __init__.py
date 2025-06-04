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

    app.config['MAIL_SERVER'] = 'smtp.example.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your_email@example.com'
    app.config['MAIL_PASSWORD'] = 'your_password'
    mail.init_app(app)
    
    
    # Import models to ensure they are registered with SQLAlchemy
    from models.user import User

    # Import blueprints to register them
    from routes.auth import auth
    from routes import main
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')

    return app



