


from models.user import User
from flask_mail import Message
from flask_mail import Mail




from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db
from models.user import User



product = Blueprint('product', __name__)

# Product listing
@product.route('/product_listing')
def product_listing():
    return render_template('/product/product_listing.html')




# product description




# product addition




# product deletion



# product update




# product search
@product.route('/product_search', methods=['GET', 'POST'])
def product_search():
    # if request.method == 'POST':
    #     search_query = request.form.get('search_query')
    #     # Here you would typically query your database for products matching the search query
    #     # For now, we'll just flash a message
    #     flash(f'Searching for products related to: {search_query}')
    #     return redirect(url_for('product.product_listing'))
    return render_template('/product/product_search.html')






# product 






