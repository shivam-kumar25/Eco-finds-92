from models.models import User, Product, Order, OrderItem, Review
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from sqlalchemy import desc
from __init__ import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from PIL import Image




user = Blueprint('user', __name__)

# Add configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'profile_pictures')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@user.route('/home')
def index():
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to access dashboard', 'warning')
        return redirect(url_for('auth.login'))

    # Get user data
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.login'))

    # Get user statistics
    stats = {
        'active_listings': Product.query.filter_by(seller_id=user_id, status='active').count(),
        'items_sold': Order.query.filter_by(seller_id=user_id, status='completed').count(),
        'messages': 0,  # Implement message count when messaging system is added
        'reviews': Review.query.filter_by(seller_id=user_id).count()
    }

    # Get recent listings
    recent_listings = Product.query.filter_by(seller_id=user_id)\
        .order_by(Product.created_at.desc())\
        .limit(3)\
        .all()

    # Get community spotlights (you might want to implement this differently)
    community_spotlights = [
        {
            'icon': '💡',
            'message': 'I found a rare vinyl record here and connected with a fellow collector!',
            'author': 'Alex M.'
        },
        {
            'icon': '🌿',
            'message': 'Selling my old camera gave it a second life and helped me declutter!',
            'author': 'Lauren S.'
        },
        {
            'icon': '🔄',
            'message': 'I love supporting local sellers and reducing waste through reuse.',
            'author': 'Michael T.'
        }
    ]

    return render_template(
        'user/home.html',
        title='Welcome to EcoFinds',
        current_user=user,
        stats=stats,
        recent_listings=recent_listings,
        community_spotlights=community_spotlights
    )









# Profile setup

@user.route('/profile_setup', methods=['GET', 'POST'])
def profile_setup():
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to setup your profile', 'warning')
        return redirect(url_for('auth.login'))

    # Get user data
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            # Handle profile picture upload
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"user_{user_id}_{file.filename}")
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    
                    # Save and resize image
                    image = Image.open(file)
                    image.thumbnail((300, 300))  # Resize to max dimensions
                    image.save(filepath)
                    
                    # Update user profile picture path
                    user.profile_picture = f'/static/uploads/profile_pictures/{filename}'

            # Update user information
            user.full_name = request.form.get('full_name')
            user.username = request.form.get('username')
            user.email = request.form.get('email')
            user.phone_number = request.form.get('phone_number')
            user.bio = request.form.get('bio')
            user.communication_preferences = request.form.get('communication_preferences')
            user.preferred_language = request.form.get('preferred_language')
            user.address = request.form.get('address')

            # Save changes to database
            db.session.commit()

            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.profile'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
            return redirect(url_for('user.profile_setup'))

    # GET request - display form
    return render_template(
        'user/profile_setup.html',
        title='Profile Setup',
        user=user
    )



# profile 
@user.route('/profile')
def profile():
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to view your profile', 'warning')
        return redirect(url_for('auth.login'))

    # Get user data
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.login'))

    # Get user statistics
    stats = [
        {
            'icon': '📦',
            'title': 'Active Listings',
            'value': Product.query.filter_by(seller_id=user_id, status='active').count()
        },
        {
            'icon': '💰',
            'title': 'Items Sold',
            'value': Order.query.filter_by(seller_id=user_id, status='completed').count()
        },
        {
            'icon': '⭐',
            'title': 'Reviews',
            'value': Review.query.filter_by(seller_id=user_id).count()
        },
        {
            'icon': '🏆',
            'title': 'Rating',
            'value': f"{Review.query.filter_by(seller_id=user_id).with_entities(db.func.avg(Review.rating)).scalar() or 0:.1f}/5.0"
        }
    ]

    # Get recent listings
    recent_listings = Product.query.filter_by(seller_id=user_id)\
        .order_by(Product.created_at.desc())\
        .limit(3)\
        .all()

    # Get recent reviews
    recent_reviews = Review.query.filter_by(seller_id=user_id)\
        .join(User, User.id == Review.reviewer_id)\
        .add_columns(
            Review.rating,
            Review.text,
            User.username.label('author')
        )\
        .order_by(Review.created_at.desc())\
        .limit(3)\
        .all()

    # Format reviews for template
    formatted_reviews = [{
        'rating': review.rating,
        'text': review.text,
        'author': review.author
    } for review in recent_reviews]

    return render_template(
        'user/profile.html',
        title='My Profile',
        current_user=user,
        stats=stats,
        recent_listings=recent_listings,
        recent_reviews=formatted_reviews
    )



@user.route('/previous_purchases')
def previous_purchases():
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to view your purchases', 'warning')
        return redirect(url_for('auth.login'))

    # Get user data
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.login'))

    # Get user's purchases with related data
    purchases = Order.query.filter_by(user_id=user_id)\
        .join(OrderItem)\
        .join(Product)\
        .join(User, Product.seller_id == User.id)\
        .join(Review, (Review.order_id == Order.id) & (Review.reviewer_id == user_id), isouter=True)\
        .add_columns(
            Order.id,
            Order.created_at.label('purchase_date'),
            OrderItem.price,
            Product.name,
            Product.image_url,
            User.username.label('seller_name'),
            Review.id.label('review_id')
        )\
        .order_by(desc(Order.created_at))\
        .all()

    # Format purchase data for template
    formatted_purchases = [{
        'id': p.id,
        'purchase_date': p.purchase_date,
        'price': p.price,
        'product': {
            'name': p.name,
            'image_url': p.image_url
        },
        'seller': {
            'username': p.seller_name
        },
        'is_reviewed': bool(p.review_id)
    } for p in purchases]

    return render_template(
        'user/previous_purchase.html',
        title='Previous Purchases',
        purchases=formatted_purchases,
        current_user=user
    )








