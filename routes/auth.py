from models.models import User
from flask_mail import Message
import random
from datetime import datetime, timedelta
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import jsonify, current_app

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db, mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature




auth = Blueprint('auth', __name__)












def generate_otp():
    """Generate a 6-digit OTP"""
    otp = str(random.randint(100000, 999999))
    print(f"DEBUG: Generated OTP: {otp}")  # Debug print
    return otp


@auth.route('/send_otp', methods=['POST', 'GET'])
def send_otp():
    try:
        # Handle both JSON and form data
        if request.is_json:
            email = request.json.get('email')
        else:
            email = request.form.get('email')
            
        if not email:
            current_app.logger.warning("OTP request without email")
            print("DEBUG: OTP request without email")
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            current_app.logger.warning(f"Invalid email format: {email}")
            print(f"DEBUG: Invalid email format: {email}")
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400

        # Generate OTP
        otp = generate_otp()
        current_app.logger.info(f"Generated OTP for {email}: {otp}")
        print(f"DEBUG: Generated OTP for {email}: {otp}")
        
        # Store OTP and timestamp in session
        session['otp'] = otp
        session['otp_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session['email'] = email
        
        print(f"DEBUG: Session data - OTP: {session.get('otp')}, Time: {session.get('otp_time')}, Email: {session.get('email')}")

        # Create HTML email template
        html_content = render_template(
            'email/otp_email.html',
            otp=otp
        )
          # Validate mail configuration
        mail_check = check_mail_config()
        print(f"DEBUG: Mail configuration validation: {mail_check}")
        
        if not mail_check['is_valid']:
            print(f"DEBUG WARNING: Mail configuration issues found: {mail_check['errors']}")
            flash(f"WARNING: Email configuration issues detected: {', '.join(mail_check['errors'])}", 'warning')
        
        try:
            # Create message
            message = Message(
                subject="Your EcoFinds Verification Code",
                recipients=[email],
                html=html_content
            )

            # Send email with detailed logging
            current_app.logger.info(f"Attempting to send OTP email to {email}")
            print(f"DEBUG: Attempting to send OTP email to {email}")
            
            mail.send(message)
            
            current_app.logger.info(f"OTP email successfully sent to {email}")
            print(f"DEBUG: OTP email successfully sent to {email}")
            
            # Always show OTP in development mode
            if current_app.config.get('DEBUG', False):
                return jsonify({
                    'success': True,
                    'message': f'OTP sent successfully. DEBUG MODE: Your OTP is {otp}',
                    'otp': otp  # Include OTP in response for debugging
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'message': 'OTP sent successfully'
                }), 200
                
        except Exception as mail_error:            # Detailed error logging
            error_msg = str(mail_error)
            current_app.logger.error(f"Email sending failed: {error_msg}")
            print(f"DEBUG ERROR: Email sending failed: {error_msg}")
            
            # Get mail config for debugging
            mail_check = check_mail_config()
            current_app.logger.error(f"Mail server config: {mail_check['config']}")
            
            # For testing/development purposes, we'll still return the OTP
            return jsonify({
                'success': False,
                'message': f'Email sending failed: {error_msg}',
                'debug_info': {
                    'error': error_msg,
                    'otp': otp,  # Include OTP in response for testing
                    'mail_config': mail_check['config'],
                    'mail_errors': mail_check['errors'] if 'errors' in mail_check else []
                }
            }), 500
            
    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Error sending OTP: {str(e)}")
        print(f"DEBUG CRITICAL ERROR: {str(e)}")
        
        return jsonify({
            'success': False,
            'message': f'Failed to send OTP: {str(e)}'
        }), 500


@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'GET':
        email = session.get('email', '')
        print(f"DEBUG: Showing OTP verification page for email: {email}")
        
        # Debug: Show current OTP in session for development
        if current_app.config.get('DEBUG', False):
            current_otp = session.get('otp')
            print(f"DEBUG: Current OTP in session for {email}: {current_otp}")
            flash(f"DEBUG MODE: Your OTP is {current_otp}", 'info')
            
        return render_template('auth/verify_otp.html', email=email)
        
    try:
        user_otp = request.form.get('otp') or request.json.get('otp')
        print(f"DEBUG: User entered OTP: {user_otp}")
        
        if not user_otp:
            print("DEBUG ERROR: OTP not provided in request")
            flash('OTP is required', 'danger')
            return render_template('auth/verify_otp.html', email=session.get('email', '')), 400

        stored_otp = session.get('otp')
        stored_time = session.get('otp_time')
        stored_email = session.get('email')
        
        print(f"DEBUG: Session data - Stored OTP: {stored_otp}, Time: {stored_time}, Email: {stored_email}")

        if not all([stored_otp, stored_time, stored_email]):
            print("DEBUG ERROR: Missing OTP session data")
            flash('No OTP request found. Please try again.', 'danger')
            return render_template('auth/verify_otp.html', email=session.get('email', '')), 400

        # Check if OTP is expired (5 minutes)
        otp_time = datetime.strptime(stored_time, '%Y-%m-%d %H:%M:%S')
        time_diff = datetime.now() - otp_time
        print(f"DEBUG: OTP age: {time_diff.total_seconds()} seconds")
        
        if time_diff > timedelta(minutes=5):
            print("DEBUG: OTP expired")
            session.pop('otp', None)
            session.pop('otp_time', None)
            flash('OTP expired. Please request a new one.', 'danger')
            return render_template('auth/verify_otp.html', email=stored_email), 400

        if user_otp == stored_otp:
            print(f"DEBUG: OTP verified successfully for {stored_email}")
            # Create an account if email doesn't exist
            user = User.query.filter_by(email=stored_email).first()
            
            if not user and 'register_data' in session:
                # Get registration data from session
                reg_data = session.get('register_data', {})
                print(f"DEBUG: Creating new user with username: {reg_data.get('username', '')}")
                
                new_user = User(
                    username=reg_data.get('username', ''),
                    email=stored_email,
                    is_active=True,
                    is_admin=False,
                    full_name=reg_data.get('full_name', ''),
                    bio='',
                    profile_picture='',
                    phone_number=reg_data.get('phone', ''),
                    address='',
                    communication_preferences={},
                    preferred_language='en',
                    category_preferences=[]
                )
                new_user.password = reg_data.get('password', '')
                
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    print(f"DEBUG: New user created with ID: {new_user.id}")
                    
                    # Store user in session
                    session['user_id'] = new_user.id
                    session['username'] = new_user.username
                    session['email'] = new_user.email
                    
                    # Clear OTP data
                    session.pop('otp', None)
                    session.pop('otp_time', None)
                    session.pop('email', None)
                    session.pop('register_data', None)
                    
                    flash('Registration successful! Welcome to EcoFinds!', 'success')
                    return redirect(url_for('user.profile'))
                except Exception as db_error:
                    print(f"DEBUG ERROR: Database error while creating user: {str(db_error)}")
                    db.session.rollback()
                    flash('Error creating account. Please try again.', 'danger')
                    return render_template('auth/verify_otp.html', email=stored_email), 500
            else:
                # For login verification
                if user:
                    print(f"DEBUG: User {user.username} logged in successfully")
                    # Store user in session
                    session['user_id'] = user.id
                    session['username'] = user.username
                    session['email'] = user.email
                    
                    # Clear OTP data
                    session.pop('otp', None)
                    session.pop('otp_time', None)
                    session.pop('email', None)
                    
                    flash('Login successful! Welcome back to EcoFinds!', 'success')
                    return redirect(url_for('user.profile'))
                else:
                    print(f"DEBUG ERROR: User with email {stored_email} not found")
                    flash('User not found. Please register first.', 'danger')
                    return redirect(url_for('auth.register'))
        else:
            print(f"DEBUG ERROR: Invalid OTP. User entered: {user_otp}, Stored: {stored_otp}")
            flash('Invalid OTP. Please try again.', 'danger')
            
            # For debugging in development mode
            if current_app.config.get('DEBUG', False):
                flash(f"Debug info - Your entered: {user_otp}, Correct OTP: {stored_otp}", 'warning')
                
            return render_template('auth/verify_otp.html', email=stored_email)

    except Exception as e:
        print(f"DEBUG CRITICAL ERROR in verify_otp: {str(e)}")
        current_app.logger.error(f"Error verifying OTP: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
        
        # Show more details in development mode
        if current_app.config.get('DEBUG', False):
            flash(f"Error details: {str(e)}", 'warning')
            
        return render_template('auth/verify_otp.html', email=session.get('email', ''))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('user.profile'))

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            phone = request.form.get('phone', '')
            full_name = request.form.get('full_name', '')

            print(f"DEBUG: Registration attempt - Username: {username}, Email: {email}")

            # Form validation
            if not all([username, email, password, confirm_password]):
                print("DEBUG ERROR: Missing required registration fields")
                flash('All required fields are required', 'danger')
                return render_template('auth/register.html', title='Register')

            if password != confirm_password:
                print("DEBUG ERROR: Passwords don't match")
                flash('Passwords do not match', 'danger')
                return render_template('auth/register.html', title='Register')

            if User.query.filter_by(username=username).first():
                print(f"DEBUG ERROR: Username '{username}' already taken")
                flash('Username already taken', 'danger')
                return render_template('auth/register.html', title='Register')

            if User.query.filter_by(email=email).first():
                print(f"DEBUG ERROR: Email '{email}' already registered")
                flash('Email already registered', 'danger')
                return render_template('auth/register.html', title='Register')            # Store registration data in session
            registration_data = {
                'username': username,
                'email': email,
                'password': password,
                'phone': phone,
                'full_name': full_name
            }
            
            print(f"DEBUG: Registration data for {email} - bypassing OTP verification")
            
            # Bypass OTP and directly create the user account
            try:
                new_user = User(
                    username=username,
                    email=email,
                    is_active=True,
                    is_admin=False,
                    full_name=full_name,
                    bio='',
                    profile_picture='',
                    phone_number=phone,
                    address='',
                    communication_preferences={},
                    preferred_language='en',
                    category_preferences=[]
                )
                new_user.password = password
                
                db.session.add(new_user)
                db.session.commit()
                print(f"DEBUG: New user created with ID: {new_user.id} (OTP bypassed)")
                
                # Store user in session
                session['user_id'] = new_user.id
                session['username'] = new_user.username
                session['email'] = new_user.email
                session['is_admin'] = new_user.is_admin
                
                flash('Registration successful! Welcome to EcoFinds!', 'success')
                return redirect(url_for('user.profile'))
            except Exception as db_error:
                error_msg = str(db_error)
                print(f"DEBUG ERROR: Database error while creating user: {error_msg}")
                db.session.rollback()
                flash(f'Error creating account: {error_msg}. Please try again.', 'danger')
                return render_template('auth/register.html', title='Register')

        except Exception as e:
            error_msg = str(e)
            current_app.logger.error(f"Registration error: {error_msg}")
            print(f"DEBUG CRITICAL ERROR in registration: {error_msg}")
            flash('An error occurred during registration. Please try again.', 'danger')
            if current_app.config.get('DEBUG', False):
                flash(f"Error details: {error_msg}", 'warning')
            return render_template('auth/register.html', title='Register')

    return render_template('auth/register.html', title='Register')






@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('user.profile'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        print(f"DEBUG: Login attempt - Email: {email}")
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"DEBUG ERROR: User with email {email} not found")
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html', title='Login')
            
        if user.verify_password(password):
            print(f"DEBUG: Password verified for {email}")
            
            # Bypass OTP verification for all logins
            print(f"DEBUG: Login success for {email}, User ID: {user.id} (OTP bypassed)")
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            session['is_admin'] = user.is_admin
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user.profile'))
        else:
            print(f"DEBUG ERROR: Invalid password for {email}")
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', title='Login')

@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('intro.index'))






@auth.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'warning')
        return redirect(url_for('auth.login'))
    # Redirect to user dashboard
    return redirect(url_for('user.profile'))

@auth.route('/test-mail', methods=['GET'])
def test_mail():
    """
    Test route to check mail functionality directly.
    Visit /auth/test-mail?email=your@email.com to test
    """
    try:
        email = request.args.get('email', 'roxxkk786@gmail.com')
        
        # Generate a test OTP
        test_otp = generate_otp()
        
        # Get mail configuration for debug
        mail_config = {
            'server': current_app.config.get('MAIL_SERVER'),
            'port': current_app.config.get('MAIL_PORT'),
            'username': current_app.config.get('MAIL_USERNAME'),
            'use_tls': current_app.config.get('MAIL_USE_TLS'),
            'password_length': len(current_app.config.get('MAIL_PASSWORD', '')) if current_app.config.get('MAIL_PASSWORD') else 0
        }
        
        # Create HTML content
        html_content = f"""
        <html>
            <body>
                <h2>Test Email from EcoFinds</h2>
                <p>This is a test email to verify that your mail configuration is working correctly.</p>
                <p>Test OTP: <strong>{test_otp}</strong></p>
                <p>Mail Config:</p>
                <ul>
                    <li>Server: {mail_config['server']}</li>
                    <li>Port: {mail_config['port']}</li>
                    <li>Username: {mail_config['username']}</li>
                    <li>TLS: {mail_config['use_tls']}</li>
                    <li>Password Length: {mail_config['password_length']} characters</li>
                </ul>
            </body>
        </html>
        """
        
        # Create message
        message = Message(
            subject="EcoFinds Mail Test",
            recipients=[email],
            html=html_content
        )
        
        print(f"Attempting to send test email to {email}...")
        mail.send(message)
        print(f"Test email successfully sent to {email}")
        
        return jsonify({
            'success': True,
            'message': f'Test email sent to {email}',
            'config': mail_config,
            'test_otp': test_otp
        })
        
    except Exception as e:
        error_message = str(e)
        print(f"ERROR sending test email: {error_message}")
        return jsonify({
            'success': False,
            'error': error_message,
            'config': mail_config if 'mail_config' in locals() else 'Not available'
        })

def check_mail_config():
    """Check mail configuration and return status"""
    mail_config = {
        'server': current_app.config.get('MAIL_SERVER'),
        'port': current_app.config.get('MAIL_PORT'),
        'username': current_app.config.get('MAIL_USERNAME'),
        'password': current_app.config.get('MAIL_PASSWORD'),
        'use_tls': current_app.config.get('MAIL_USE_TLS'),
        'use_ssl': current_app.config.get('MAIL_USE_SSL')
    }
    
    errors = []
    
    # Basic validation
    if not mail_config['server']:
        errors.append('Mail server not configured')
    
    if not mail_config['port']:
        errors.append('Mail port not configured')
        
    if not mail_config['username']:
        errors.append('Mail username not configured')
    
    if not mail_config['password']:
        errors.append('Mail password not configured')
        
    # Check if we're using Gmail but with incorrect port/security
    if 'gmail' in mail_config['server'].lower():
        if mail_config['port'] != 587 and mail_config['port'] != 465:
            errors.append(f"Gmail typically uses port 587 (TLS) or 465 (SSL), found {mail_config['port']}")
            
        if mail_config['port'] == 587 and not mail_config['use_tls']:
            errors.append('Gmail with port 587 should use TLS')
            
        if mail_config['port'] == 465 and not mail_config['use_ssl']:
            errors.append('Gmail with port 465 should use SSL')
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'config': {k: v for k, v in mail_config.items() if k != 'password'}  # Exclude password from debug output
    }

@auth.route('/admin/force-otp/<email>')
def admin_force_otp(email):
    """
    Admin route to force send an OTP to any email for testing.
    Only works in DEBUG mode.
    """
    if not current_app.config.get('DEBUG', False):
        return jsonify({
            'success': False,
            'message': 'This endpoint is only available in DEBUG mode'
        }), 403
        
    try:
        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
            
        # Generate OTP
        otp = generate_otp()
        
        # Store in session
        session['otp'] = otp
        session['otp_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session['email'] = email
        
        # Create both plain text and HTML content
        text_content = f"Your EcoFinds verification code is: {otp}"
        html_content = render_template('email/otp_email.html', otp=otp)
        
        # Create message
        message = Message(
            subject="EcoFinds Admin Forced OTP",
            recipients=[email],
            body=text_content,
            html=html_content
        )
        
        # Send email
        mail.send(message)
        
        return jsonify({
            'success': True,
            'message': f'Force sent OTP to {email}',
            'otp': otp
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500




