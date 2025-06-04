from models.user import User
from flask_mail import Message
from flask_mail import Mail




from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db
from models.user import User




auth = Blueprint('auth', __name__)

# Initialize Flask-Mail (add this after db import)
mail = Mail()

def send_welcome_email(user_email, username):
    msg = Message(
        subject="Welcome to EmpowerHer!",
        recipients=[user_email],
        body=f"Hello {username},\n\nThank you for registering at EmpowerHer. We're excited to have you on board!\n\nBest regards,\nEmpowerHer Team"
    )
    mail.send(msg)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Form validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('register.html', title='Register')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html', title='Register')

        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('register.html', title='Register')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html', title='Register')

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Send welcome email
        send_welcome_email(email, username)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', title='Login')

@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))






@auth.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'warning')
        return redirect(url_for('auth.login'))
    # Redirect to user dashboard
    return redirect(url_for('main.user_dashboard'))







