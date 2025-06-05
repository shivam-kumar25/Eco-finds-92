from models.models import User
from flask_mail import Message
from flask_mail import Mail
import random




from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app




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

def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verify')

def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verify', max_age=expiration)
    except (SignatureExpired, BadSignature):
        return None
    return email


def generate_otp():
    return str(random.randint(100000, 999999))

def send_verification_otp(user_email, username, otp):
    msg = Message(
        subject="EcoFinds Email Verification OTP",
        recipients=[user_email],
        body=f"Hello {username},\n\nYour OTP for email verification is: {otp}\n\nIf you did not register, please ignore this email.\n\nBest,\nEcoFinds Team"
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
            return render_template('auth/register.html', title='Register')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html', title='Register')

        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('auth/register.html', title='Register')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('/auth/register.html', title='Register')

        # Create new user (not yet verified)
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Generate OTP and store in session
        otp = generate_otp()
        session['pending_verification_email'] = email
        session['pending_verification_username'] = username
        session['pending_verification_otp'] = otp

        # Send OTP email
        send_verification_otp(email, username, otp)

        flash('Registration successful! Please check your email for the OTP to verify your account.', 'success')
        return redirect(url_for('auth.verify_otp'))

    return render_template('auth/register.html', title='Register'  )

@auth.route('/verify', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_verification_email' not in session:
        flash('No verification in progress.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        input_otp = request.form.get('otp')
        if input_otp == session.get('pending_verification_otp'):
            user = User.query.filter_by(email=session['pending_verification_email']).first()
            if user:
                # If you have an is_verified field, set it here
                # user.is_verified = True
                # db.session.commit()
                flash('Your email has been verified! You can now log in.', 'success')
            else:
                flash('User not found.', 'danger')
            # Clear verification session data
            session.pop('pending_verification_email', None)
            session.pop('pending_verification_username', None)
            session.pop('pending_verification_otp', None)
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    return render_template('auth/verify_otp.html', title='Verify Email')







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
    
    return render_template('auth/login.html', title='Login')

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

@auth.route('/verify/<token>')
def verify_email(token):
    email = confirm_verification_token(token)
    if not email:
        flash('The verification link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Account not found.', 'danger')
        return redirect(url_for('auth.login'))
    # You can add a field like user.is_verified = True and save it
    # user.is_verified = True
    # db.session.commit()
    flash('Your email has been verified! You can now log in.', 'success')
    return redirect(url_for('auth.login'))







