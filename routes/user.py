


from models.user import User
from flask_mail import Message
from flask_mail import Mail




from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db
from models.user import User



user = Blueprint('user', __name__)

# Profile setup

@user.route('/profile_setup')
def profile_setup():
    user_id = session.get('user_id')
    # if not user_id:
    #     return redirect(url_for('auth.login'))

    # user = User.query.get(user_id)
    return render_template('/user/profile_setup.html', title='User Profile', user=user)







# profile 
@user.route('/profile')
def profile():
    # user_id = session.get('user_id')
    # if not user_id:
    #     return redirect(url_for('auth.login'))

    # user = User.query.get(user_id)
    # if not user:
    #     flash('User not found', 'danger')
    #     return redirect(url_for('auth.login'))

    return render_template('/user/profile.html', title='User Profile', user=user)








