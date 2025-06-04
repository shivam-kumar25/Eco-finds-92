from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(128), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(256), nullable=True)  # New field for profile picture path or URL
    phone_number = db.Column(db.String(20), nullable=True)  # New field for phone number
    address = db.Column(db.String(256), nullable=True)  # New field for address
    communication_preferences = db.Column(db.String(256), nullable=True)  # New field for communication preferences
    preferred_language = db.Column(db.String(64), nullable=True)  # New field for preferred language
    category_preferences = db.Column(db.String(256), nullable=True)  # New field for category preferences
    


    # # Relationships
    # products = db.relationship('Product', backref='seller', lazy='dynamic')
    # cart_items = db.relationship('CartItem', backref='user', lazy='dynamic')
    # orders = db.relationship('Order', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'







