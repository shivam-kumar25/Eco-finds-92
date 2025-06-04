


from models.user import User
from flask_mail import Message
from flask_mail import Mail




from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db
from models.user import User




payment = Blueprint('payment', __name__)


@payment.route('/payment', methods=['GET', 'POST'])
def checkout():
#     if request.method == 'POST':
#         # Process the payment here
#         # For example, you can use a payment gateway API to handle the transaction
#         # This is a placeholder for actual payment processing logic
#         flash('Payment processed successfully!', 'success')
#         return redirect(url_for('main.index'))

    return render_template('payment/payment_page.html', title='Payment')


