from models.models import User
from flask_mail import Message
from flask_mail import Mail





from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db



product = Blueprint('product', __name__)

# Product listing
@product.route('/product_listing')
def product_listing():
    from models.models import Product, Category
    
    # Get all categories for the filter
    categories = Category.query.all()
    
    # Get selected category filter
    category_id = request.args.get('category_id', type=int)
    
    # Base query for active, non-deleted products
    query = Product.query.filter(
        (Product.status == 'active') &
        (Product.is_deleted == False)
    )
    
    # Apply category filter if selected
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # Execute query and get products
    products = query.all()
    
    return render_template('/product/product_listing.html', 
                          products=products,
                          categories=categories,
                          selected_category_id=category_id)




# product details
@product.route('/product_details/<int:product_id>')
def product_details(product_id):
    from models.models import Product, Auction
    
    # Fetch the product by ID
    product = Product.query.get_or_404(product_id)
    
    # Check if this product has an active auction
    auction = Auction.query.filter_by(
        product_id=product_id,
        status='active'
    ).first()
    
    # If there's an auction, redirect to the auction details page
    if auction:
        return redirect(url_for('auction.auction_details', auction_id=auction.id))
    
    return render_template('/product/product_details.html', product=product)




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
    from models.models import Product
    
    products = []
    search_query = request.args.get('query', '')
    
    if search_query:
        # Search in product titles and descriptions
        products = Product.query.filter(
            (Product.name.ilike(f'%{search_query}%') | 
             Product.description.ilike(f'%{search_query}%')) &
            (Product.status == 'active') &
            (Product.is_deleted == False)
        ).all()
    
    return render_template('/product/search.html', 
                          products=products, 
                          search_query=search_query)



 


# product category page
@product.route('/category')
def product_category():
    return render_template('/product/category.html')






# Tendy Products
@product.route('/trendy_products')
def trendy_products():
    return render_template('/product/trendy_products.html')


# Product browsing for public users
@product.route('/browse')
def browse():
    from models.models import Product, Category
    
    # Get all categories for the filter
    categories = Category.query.all()
    
    # Get selected category filter
    category_id = request.args.get('category_id', type=int)
    
    # Base query for active, non-deleted products
    query = Product.query.filter(
        (Product.status == 'active') &
        (Product.is_deleted == False)
    )
    
    # Apply category filter if selected
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # Execute query and get products
    products = query.all()
    
    return render_template('product/category.html', 
                          title='Browse Products',
                          products=products,
                          categories=categories,
                          selected_category_id=category_id)


