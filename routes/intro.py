
from models.user import User
from flask_mail import Message
from flask_mail import Mail




from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db
from models.user import User



intro = Blueprint('intro', __name__)


@intro.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    
    return render_template('intro.html', title='Welcome to Eco-Finds 92')


