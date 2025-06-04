
from models.user import User
from flask_mail import Message
from flask_mail import Mail




from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db
from models.user import User



home = Blueprint('home', __name__)


@home.route('/user/home')
def index():
    user_name = session.get('user_name')
    return render_template('home.html', title='Welcome to Eco-Finds 92', user_name=user_name)

