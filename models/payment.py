from datetime import datetime
from __init__ import db

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    payment_method = db.Column(db.String(50), nullable=False)  # e.g., 'credit_card', 'paypal'
    status = db.Column(db.String(20), default='pending')  # e.g., 'pending', 'completed', 'failed'
    transaction_id = db.Column(db.String(128), unique=True, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(256), nullable=True)

    user = db.relationship('User', backref=db.backref('payments', lazy='dynamic'))

    def __repr__(self):
        return f"<Payment {self.id} - User {self.user_id} - {self.amount} {self.currency} - {self.status}>"








