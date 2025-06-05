

from models.models import User
from flask_mail import Message
from flask_mail import Mail
import random




from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db



auction = Blueprint('auction', __name__)

# route for the auction page showing the live auction items
@auction.route('/live')
def auction_page():
    user_name = session.get('user_name')
    return render_template('auction/live_auction.html', title='Auction Page', user_name=user_name)




@auction.route('/create', methods=['GET', 'POST'])
def create_auction():
    if request.method == 'POST':
        # Handle auction creation logic here
        pass
    return render_template('auction/create_auction.html', title='Create Auction')








# Route for auction details page for a specific auction item (live)
@auction.route('/details/<int:auction_id>')
def auction_details(auction_id):
    user_name = session.get('user_name')
    return render_template('auction/auction_details.html', title='Auction Details', user_name=user_name, auction_id=auction_id)




# Route for auction details page for a specific auction item (upcoming)
@auction.route('/details/upcoming/<int:auction_id>')
def upcoming_auction_details(auction_id):
    user_name = session.get('user_name')
    return render_template('auction/product_auction_details.html', title='Upcoming Auction Details', user_name=user_name, auction_id=auction_id)



# Route for auction registration page
@auction.route('/register', methods=['GET', 'POST'])
def auction_register():
    if request.method == 'POST':
        # Handle registration logic here
        pass
    return render_template('auction/auction_registration.html', title='Auction Registration')


# Route for auction bid success page
@auction.route('/bid/success/<int:auction_id>')
def bid_success(auction_id):
    user_name = session.get('user_name')
    return render_template('auction/bid_success.html', title='Bid Success', user_name=user_name, auction_id=auction_id)


# Route for auction bid failure page
@auction.route('/bid/failure/<int:auction_id>')
def bid_failure(auction_id):
    user_name = session.get('user_name')
    return render_template('auction/bid_failure.html', title='Bid Failure', user_name=user_name, auction_id=auction_id)



# route for auction checkout page
@auction.route('/checkout/<int:auction_id>', methods=['GET', 'POST']) 
def auction_checkout(auction_id):
#     user_name = session.get('user_name')
#     if request.method == 'POST':
#         # Handle checkout logic here
#         flash('Checkout successful!', 'success')
#         return redirect(url_for('auction.bid_success', auction_id=auction_id))
    return render_template('auction/bid_checkout.html', title='Auction Checkout', auction_id=auction_id)




# 


