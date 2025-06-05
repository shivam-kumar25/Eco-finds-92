from models.models import User, Auction, Bid, Product, AuctionRegistration
from flask_mail import Message, Mail
import random
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db



auction = Blueprint('auction', __name__)

# route for the auction page showing the live auction items
@auction.route('/live')
def auction_page():
    # Get all active auctions
    active_auctions = Auction.query.filter_by(
        status='active'
    ).order_by(
        Auction.end_date.asc()  # Show auctions ending soon first
    ).all()
    
    # Prepare auction data with additional information
    auctions_data = []
    for auction_item in active_auctions:
        # Get highest bid if any
        highest_bid = Bid.query.filter_by(
            auction_id=auction_item.id
        ).order_by(
            Bid.amount.desc()
        ).first()
        
        # Get bidder count
        bidder_count = Bid.query.filter_by(
            auction_id=auction_item.id
        ).with_entities(
            Bid.bidder_id
        ).distinct().count()
        
        # Get time remaining in minutes
        if auction_item.end_date > datetime.utcnow():
            time_remaining = auction_item.end_date - datetime.utcnow()
            time_remaining_minutes = int(time_remaining.total_seconds() / 60)
        else:
            time_remaining_minutes = 0
        
        # Add to auction data
        auctions_data.append({
            'auction': auction_item,
            'highest_bid': highest_bid.amount if highest_bid else auction_item.start_price,
            'bidder_count': bidder_count,
            'time_remaining_minutes': time_remaining_minutes,
            'product': auction_item.product,
            'seller': auction_item.seller
        })
    
    return render_template(
        'auction/live_auction.html', 
        title='Live Auctions', 
        auctions=auctions_data,
        user_id=session.get('user_id')
    )




@auction.route('/create', methods=['GET', 'POST'])
def create_auction():
    from models.models import Auction, Product
    from datetime import datetime, timedelta
    
    if 'user_id' not in session:
        flash('Please login to create an auction', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get user's products that are not in an active auction
    user_products = Product.query.filter_by(
        seller_id=session['user_id'],
        status='active',
        is_deleted=False
    ).all()
    
    valid_products = []
    for product in user_products:
        # Check if product already has an active auction
        existing_auction = Auction.query.filter_by(
            product_id=product.id,
            status='active'
        ).first()
        
        if not existing_auction:
            valid_products.append(product)
    
    if request.method == 'POST':
        product_id = request.form.get('product_id', type=int)
        start_price = request.form.get('start_price', type=float)
        reserve_price = request.form.get('reserve_price', type=float)
        duration_days = request.form.get('duration', type=int) 
        
        if not all([product_id, start_price, duration_days]):
            flash('Please fill out all required fields', 'danger')
            return render_template('auction/create_auction.html', 
                                  title='Create Auction',
                                  products=valid_products)
        
        # Verify the product belongs to the user
        product = Product.query.filter_by(
            id=product_id,
            seller_id=session['user_id']
        ).first()
        
        if not product:
            flash('Invalid product selection', 'danger')
            return redirect(url_for('auction.create'))
        
        # Create the auction
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(days=duration_days)
        
        new_auction = Auction(
            seller_id=session['user_id'],
            product_id=product_id,
            start_price=start_price,
            reserve_price=reserve_price if reserve_price else None,
            start_time=start_time,
            end_time=end_time,
            status='active',
            auto_confirm=False,
            entry_fee=0
        )
        
        db.session.add(new_auction)
        db.session.commit()
        
        flash('Auction created successfully!', 'success')
        return redirect(url_for('auction.auction_details', auction_id=new_auction.id))
    
    return render_template('auction/create_auction.html', 
                          title='Create Auction',
                          products=valid_products)








# Route for auction details page for a specific auction item (live)
@auction.route('/details/<int:auction_id>', methods=['GET', 'POST'])
def auction_details(auction_id):
    from models.models import Auction, Bid, Product
    from datetime import datetime
    
    # Get the logged-in user
    user_id = session.get('user_id')
    username = session.get('username')
    
    if not user_id:
        flash('Please login to view auction details', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get the auction
    auction = Auction.query.get_or_404(auction_id)
    
    # Get the product
    product = Product.query.get_or_404(auction.product_id)
    
    # Get current highest bid
    highest_bid = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.amount.desc()).first()
    current_bid = highest_bid.amount if highest_bid else auction.start_price
    
    # Handle bid submission
    if request.method == 'POST':
        bid_amount = request.form.get('bid_amount', type=float)
        
        if not bid_amount:
            flash('Please enter a valid bid amount', 'danger')
        elif bid_amount <= current_bid:
            flash(f'Your bid must be higher than the current bid (${current_bid})', 'danger')
            return redirect(url_for('auction.bid_failure', auction_id=auction_id))
        else:
            # Create new bid
            new_bid = Bid(
                auction_id=auction_id,
                bidder_id=user_id,
                amount=bid_amount,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(new_bid)
            db.session.commit()
            
            flash('Your bid has been placed successfully!', 'success')
            return redirect(url_for('auction.bid_success', auction_id=auction_id))
    
    # Get all bids for this auction
    bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.timestamp.desc()).all()
    
    # Calculate time remaining
    time_remaining = auction.end_time - datetime.utcnow()
    
    return render_template(
        'auction/product_auction_details.html',
        title='Auction Details',
        username=username,
        auction=auction,
        product=product,
        current_bid=current_bid,
        bids=bids,
        time_remaining=time_remaining
    )




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


