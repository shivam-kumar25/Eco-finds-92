from datetime import datetime
from typing import Optional, List
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from __init__ import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SoftDeleteMixin:
    deleted_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)

class User(db.Model, TimestampMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(128))
    bio = db.Column(db.Text)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    profile_picture = db.Column(db.String(256))
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(256))
    communication_preferences = db.Column(db.JSON, default={})
    preferred_language = db.Column(db.String(64), default='en')
    category_preferences = db.Column(db.JSON, default=[])

    # Relationships with cascade delete
    products = relationship('Product', backref='seller', lazy='dynamic', 
                          cascade='all, delete-orphan')
    orders = relationship('Order', backref='user', lazy='dynamic',
                         cascade='all, delete-orphan')
    cart_items = relationship('CartItem', backref='user', lazy='dynamic',
                            cascade='all, delete-orphan')
    bids = relationship('Bid', back_populates='bidder', lazy='dynamic',
                       cascade='all, delete-orphan')
    notifications = relationship('Notification', backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    auctions_created = relationship('Auction', backref='seller', lazy='dynamic',
                                  cascade='all, delete-orphan')
    auctions_registered = relationship('AuctionRegistration', back_populates='bidder',
                                     lazy='dynamic', cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'profile_picture': self.profile_picture,
            'is_admin': self.is_admin
        }




class Product(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_filename = db.Column(db.String(200))
    condition = db.Column(db.Enum('New', 'Like New', 'Very Good', 'Good', 'Fair', 
                                name='product_condition'), 
                         default='Good')
    original_packaging = db.Column(db.Boolean, default=False)
    eco_impact_score = db.Column(db.Integer, default=3)
    estimated_co2_saved = db.Column(db.Float, default=0.0)
    status = db.Column(db.Enum('draft', 'active', 'sold', 'archived',
                              name='product_status'),
                      default='draft')

    # Foreign keys with indexes
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)

    # Relationships
    cart_items = relationship('CartItem', backref='product', lazy='dynamic',
                            cascade='all, delete-orphan')
    order_items = relationship('OrderItem', backref='product', lazy='dynamic')
    auction = relationship('Auction', back_populates='product', uselist=False,
                         cascade='all, delete-orphan')

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

class Review(db.Model, TimestampMixin):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    helpful_votes = db.Column(db.Integer, default=0)
    
    # Relationships
    reviewer = db.relationship('User', foreign_keys=[reviewer_id],
                             backref=db.backref('reviews_given', lazy='dynamic'))
    seller = db.relationship('User', foreign_keys=[seller_id],
                           backref=db.backref('reviews_received', lazy='dynamic'))
    order = db.relationship('Order', backref=db.backref('review', uselist=False))
    product = db.relationship('Product', backref=db.backref('reviews', lazy='dynamic'))

    __table_args__ = (
        # Ensure one review per order
        db.UniqueConstraint('order_id', name='uq_review_per_order'),
        # Ensure rating is between 1 and 5
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )

    def __repr__(self):
        return f'<Review {self.id} Rating={self.rating}>'

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'reviewer': self.reviewer.username,
            'rating': self.rating,
            'text': self.text,
            'created_at': self.created_at.isoformat(),
            'helpful_votes': self.helpful_votes
        }





