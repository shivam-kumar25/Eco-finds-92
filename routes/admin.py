
from models.models import User
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db
from datetime import datetime
from utils import admin_required

admin = Blueprint('admin', __name__)

# Admin dashboard
@admin.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html', title='Admin Dashboard')

# Complaints dashboard
@admin.route('/complaints')
@admin_required
def complaints():
    # Create dummy complaint data for MVP
    dummy_complaints = [
        {
            'id': 1,
            'user_name': 'JohnDoe',
            'subject': 'Item not as described',
            'item_id': 101,
            'item_name': 'Vintage Camera',
            'status': 'Open',
            'date_reported': datetime(2023, 6, 1, 10, 30)
        },
        {
            'id': 2,
            'user_name': 'JaneSmith',
            'subject': 'Delivery issue',
            'item_id': 202,
            'item_name': 'Antique Watch',
            'status': 'In Progress',
            'date_reported': datetime(2023, 6, 2, 14, 15)
        },
        {
            'id': 3,
            'user_name': 'MikeJohnson',
            'subject': 'Payment problem',
            'item_id': 303,
            'item_name': 'Wooden Chair',
            'status': 'Resolved',
            'date_reported': datetime(2023, 6, 3, 9, 45)
        },
        {
            'id': 4,
            'user_name': 'SarahWilliams',
            'subject': 'Seller not responding',
            'item_id': 404,
            'item_name': 'Ceramic Vase',
            'status': 'Open',
            'date_reported': datetime(2023, 6, 4, 16, 20)
        },
        {
            'id': 5,
            'user_name': 'DavidBrown',
            'subject': 'Refund request',
            'item_id': 505,
            'item_name': 'Vinyl Record',
            'status': 'Closed',
            'date_reported': datetime(2023, 6, 5, 11, 10)
        }
    ]
    
    # Filter complaints based on query parameters for the MVP
    status_filter = request.args.get('status')
    if status_filter:
        dummy_complaints = [c for c in dummy_complaints if c['status'].lower() == status_filter.lower()]
    
    return render_template(
        'admin/complaints.html', 
        title='Complaint Management',
        complaints=dummy_complaints
    )

# Complaint detail view
@admin.route('/complaints/<int:complaint_id>')
@admin_required
def complaint_detail(complaint_id):
    # For MVP, create a dummy complaint detail
    dummy_complaint = {
        'id': complaint_id,
        'user_name': f'User{complaint_id}',
        'user_email': f'user{complaint_id}@example.com',
        'subject': 'Sample Complaint Subject',
        'description': 'This is a detailed description of the complaint. The user has reported an issue that requires administrative attention.',
        'item_id': 100 + complaint_id,
        'item_name': f'Product {100 + complaint_id}',
        'status': 'Open',
        'date_reported': datetime.now(),
        'messages': [
            {
                'sender': f'User{complaint_id}',
                'message': 'I have a problem with this product.',
                'timestamp': datetime.now()
            },
            {
                'sender': 'Admin',
                'message': 'I understand your concern. Can you provide more details?',
                'timestamp': datetime.now()
            }
        ]
    }
    
    return render_template(
        'admin/complaint_detail.html',
        title='Complaint Details',
        complaint=dummy_complaint
    )

# Update complaint status
@admin.route('/complaints/<int:complaint_id>/update', methods=['POST'])
@admin_required
def update_complaint(complaint_id):
    new_status = request.form.get('status')
    
    if not new_status:
        flash('Please select a status', 'danger')
    else:
        # In a real application, we would update the complaint in the database
        flash(f'Complaint #{complaint_id} status updated to {new_status}', 'success')
    
    return redirect(url_for('admin.complaint_detail', complaint_id=complaint_id))
