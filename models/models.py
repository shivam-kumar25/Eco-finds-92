from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db


class User(db.Model):
    __tablename__ = 'users'
    
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
    


    # Relationships
    products = db.relationship('Product', backref='seller', lazy='dynamic')
    cart_items = db.relationship('CartItem', backref='user', lazy='dynamic')
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    bids = db.relationship('Bid', back_populates='bidder', lazy='dynamic')
    auctions_registered = db.relationship('AuctionRegistration', back_populates='bidder', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    auctions_created = db.relationship('Auction', backref='seller', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'




class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(200))
    condition = db.Column(db.String(50), default='Used - Good')
    original_packaging = db.Column(db.Boolean, default=False)
    eco_impact_score = db.Column(db.Integer, default=3)  # Scale 1-5
    estimated_co2_saved = db.Column(db.Float, default=0.0)  # in kg
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    # Fix: Remove backref from Product side, let Auction handle the relationship
    auction = db.relationship('Auction', uselist=False, back_populates='product')

    def __repr__(self):
        return f'<Product {self.name}>'




class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'







class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    total_amount = db.Column(db.Float, nullable=False)
    
    # Foreign key - Fix: change 'user.id' to 'users.id'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')
    
    def __repr__(self):
        return f'<Order {self.id}>'




class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    
    # Foreign keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'






class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys - Fix table names to match __tablename__ values
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def __repr__(self):
        return f'<CartItem {self.product_id}>'




class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Fixed: 'user.id' -> 'users.id'
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    transaction_id = db.Column(db.String(128), unique=True, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(256), nullable=True)

    user = db.relationship('User', backref=db.backref('payments', lazy='dynamic'))

    def __repr__(self):
        return f"<Payment {self.id} - User {self.user_id} - {self.amount} {self.currency} - {self.status}>"


# ----------------------------------------------------------
# Auction Model
# ----------------------------------------------------------

class Auction(db.Model):
    __tablename__ = 'auctions'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Fixed: 'product.id' -> 'products.id'
    start_price = db.Column(db.Numeric(10, 2), nullable=False)
    reserve_price = db.Column(db.Numeric(10, 2))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, active, ended, cancelled
    auto_confirm = db.Column(db.Boolean, default=False)
    entry_fee = db.Column(db.Numeric(10, 2), default=0)
    
   # Relationships
    bids = db.relationship('Bid', back_populates='auction', lazy='dynamic',
                          cascade='all, delete-orphan')
    registrations = db.relationship('AuctionRegistration', back_populates='auction',
                                  lazy='dynamic', cascade='all, delete-orphan')
    # Fix: Change backref to back_populates
    product = db.relationship('Product', back_populates='auction', uselist=False)

    def __repr__(self):
        return f'<Auction {self.id} for Product {self.product_id}>'

# ----------------------------------------------------------
# Bid Model
# ----------------------------------------------------------
class Bid(db.Model):
    __tablename__ = 'bids'
    
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    auction = db.relationship('Auction', back_populates='bids')
    bidder = db.relationship('User', back_populates='bids')

    def __repr__(self):
        return f'<Bid {self.id} Amount={self.amount}>'

# ----------------------------------------------------------
# AuctionRegistration Model
# ----------------------------------------------------------
class AuctionRegistration(db.Model):
    __tablename__ = 'auction_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    entry_fee_paid = db.Column(db.Boolean, default=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    reminder_preferences = db.Column(db.JSON)  # Store reminder preferences as JSON
    agrees_to_terms = db.Column(db.Boolean, default=False)
    
    # Relationships
    auction = db.relationship('Auction', back_populates='registrations')
    bidder = db.relationship('User', back_populates='auctions_registered')

    __table_args__ = (
        db.UniqueConstraint('auction_id', 'bidder_id', name='uq_auction_registration'),
    )


# ----------------------------------------------------------
# (Optional) Notification Model
# ----------------------------------------------------------
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # outbid, auction_ending, etc.
    message = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id} Type={self.type}>'





