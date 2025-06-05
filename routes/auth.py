from models.models import User
from flask_mail import Message
from flask_mail import Mail
import random
from datetime import datetime, timedelta
from flask_mail import Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import jsonify



from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app




auth = Blueprint('auth', __name__)












def generate_otp():
    return str(random.randint(100000, 999999))


@auth.route('/send_otp', methods=['POST', 'GET'])
def send_otp():
    try:
        # Get email from request
        email = request.json.get('email')
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400

        # Generate OTP
        otp = generate_otp()
        
        # Store OTP and timestamp in session
        session['otp'] = otp
        session['otp_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session['email'] = email

        # Create HTML email template
        html_content = render_template(
            'email/otp_email.html',
            otp=otp
        )

        # Create message
        message = Message(
            subject="Your EcoFinds Verification Code",
            recipients=[email],
            html=html_content
        )

        # Send email
        mail.send(message)

        return jsonify({
            'success': True,
            'message': 'OTP sent successfully'
        }), 200

    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Error sending OTP: {str(e)}")
        
        return jsonify({
            'success': False,
            'message': 'Failed to send OTP. Please try again.'
        }), 500
   
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")
        return f"Failed to send OTP: {str(e)}", 500


@auth.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        user_otp = request.json.get('otp')
        if not user_otp:
            return "OTP is required", 400


        stored_otp = session.get('otp')
        stored_time = session.get('otp_time')
        stored_email = session.get('email')


        if not all([stored_otp, stored_time, stored_email]):
            return "No OTP request found", 400


        # Check if OTP is expired (5 minutes)
        otp_time = datetime.strptime(stored_time, '%Y-%m-%d %H:%M:%S')
        if datetime.now() - otp_time > timedelta(minutes=5):
            session.pop('otp', None)
            session.pop('otp_time', None)
            session.pop('email', None)
            return "OTP expired", 400


        if user_otp == stored_otp:
            # Clear session after successful verification
            session.pop('otp', None)
            session.pop('otp_time', None)
            session.pop('email', None)
            return "OTP verified successfully!", 200
        else:
            return "Invalid OTP", 400


    except Exception as e:
        print(f"Error verifying OTP: {str(e)}")
        return f"Failed to verify OTP: {str(e)}", 500









@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            username = request.form.get('username')
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
                return render_template('auth/register.html', title='Register')

            # Create new user with default values
            new_user = User(
                username=username,
                email=email,
                is_active=True,  # Set default active status
                is_admin=False,  # Set default admin status
                full_name='',  # Empty default values for optional fields
                bio='',
                profile_picture='',
                phone_number='',
                address='',
                communication_preferences={},
                preferred_language='en',
                category_preferences=[]
            )
            new_user.password = password  # This will hash the password

            # Add and commit the new user
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! Please check your email for the OTP to verify your account.', 'success')
            return redirect(url_for('auth.verify_otp'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('auth/register.html', title='Register')

    return render_template('auth/register.html', title='Register'  )




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




