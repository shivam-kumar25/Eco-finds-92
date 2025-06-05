


from models.models import User
from flask_mail import Message
from flask_mail import Mail





from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db



product = Blueprint('product', __name__)

# Product listing
@product.route('/product_listing')
def product_listing():
    return render_template('/product/product_listing.html')




# product details
@product.route('/product_details')
def product_details():
    return render_template('/product/product_details.html')




# product addition
@product.route('/add_product', methods=['GET', 'POST'])
def add_product():
    # if request.method == 'POST':
    #     # Handle product addition logic here
    #     flash('Product added successfully!')
    #     return redirect(url_for('product.product_listing'))
    return render_template('/product/add_product.html')


# product deletion



# product update




# product search
@product.route('/search', methods=['GET', 'POST'])
def product_search():
    # if request.method == 'POST':
    #     search_query = request.form.get('search_query')
    #     # Here you would typically query your database for products matching the search query
    #     # For now, we'll just flash a message
    #     flash(f'Searching for products related to: {search_query}')
    #     return redirect(url_for('product.product_listing'))
    return render_template('/product/search.html')



 


# product category page
@product.route('/category')
def product_category():
    return render_template('/product/category.html')






# Tendy Products
@product.route('/trendy_products')
def trendy_products():
    return render_template('/product/trendy_products.html')


