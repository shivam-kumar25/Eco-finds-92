

from models.user import User
from flask_mail import Message
from flask_mail import Mail
import random




from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db
from models.user import User



auction = Blueprint('auction', __name__)


@auction.route('/live')
def auction_page():
    user_name = session.get('user_name')
    return render_template('/auction.html', title='Auction Page', user_name=user_name)



@auction.route('create', methods=['GET', 'POST'])
def create_auction():
    if request.method == 'POST':
        # Handle auction creation logic here
        pass
    return render_template('create_auction.html', title='Create Auction')







