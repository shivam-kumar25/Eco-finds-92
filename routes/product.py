from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db

product = Blueprint('product', __name__)

# Alias route for /listings to redirect to /product_listing
@product.route('/listings')
def listings_alias():
    return redirect(url_for('product.product_listing'))
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db

product = Blueprint('product', __name__)

# Category browse by name (for category cards)
@product.route('/categories/<category_name>')
def browse_category(category_name):
    from models.models import Product, Category
    # Find the category by name (case-insensitive)
    category = Category.query.filter(Category.name.ilike(category_name)).first()
    if not category:
        flash('Category not found.', 'warning')
        return redirect(url_for('product.product_category'))
    # Get all categories for the filter dropdown
    categories = Category.query.all()
    # Get products in this category
    products = Product.query.filter(
        (Product.category_id == category.id) &
        (Product.status == 'active') &
        (Product.is_deleted == False)
    ).all()
    return render_template('/product/search.html',
                          products=products,
                          categories=categories,
                          selected_category_id=category.id,
                          search_query='',
                          min_price=None,
                          max_price=None)
from models.models import User
from flask_mail import Message
from flask_mail import Mail





from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db



product = Blueprint('product', __name__)

# Product listing
@product.route('/product_listing')
def product_listing():
    if 'user_id' not in session:
        flash('Please login to view your listings.', 'warning')
        return redirect(url_for('auth.login'))
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
    from models.models import Product, Category
    from werkzeug.utils import secure_filename
    import os
    if 'user_id' not in session:
        flash('Please login to add a product.', 'warning')
        return redirect(url_for('auth.login'))
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_name = request.form.get('category')
        price = request.form.get('price', type=float)
        condition = request.form.get('condition')
        # Handle image upload
        images = request.files.getlist('images[]')
        if not (title and description and category_name and price and images and images[0].filename):
            flash('All fields including at least one image are required.', 'danger')
            return render_template('/product/add_product.html', categories=categories)
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            flash('Invalid category selected.', 'danger')
            return render_template('/product/add_product.html', categories=categories)
        # Save the first image (extend to multiple if needed)
        image_file = images[0]
        filename = secure_filename(image_file.filename)
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'products')
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, filename)
        image_file.save(image_path)
        # Create product
        new_product = Product(
            name=title,
            description=description,
            price=price,
            image_filename=filename,
            condition=condition,
            seller_id=session['user_id'],
            category_id=category.id,
            status='active',
            is_deleted=False
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('product.product_listing'))
    return render_template('/product/add_product.html', categories=categories)



# product deletion
@product.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    from models.models import Product
    if 'user_id' not in session:
        flash('Please login to delete a product.', 'warning')
        return redirect(url_for('auth.login'))
    product = Product.query.get_or_404(product_id)
    if product.seller_id != session['user_id']:
        flash('You are not authorized to delete this product.', 'danger')
        return redirect(url_for('product.product_listing'))
    product.is_deleted = True
    db.session.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('product.product_listing'))




# product update
@product.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    from models.models import Product, Category
    from werkzeug.utils import secure_filename
    import os
    if 'user_id' not in session:
        flash('Please login to edit a product.', 'warning')
        return redirect(url_for('auth.login'))
    product = Product.query.get_or_404(product_id)
    if product.seller_id != session['user_id']:
        flash('You are not authorized to edit this product.', 'danger')
        return redirect(url_for('product.product_listing'))
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_name = request.form.get('category')
        price = request.form.get('price', type=float)
        condition = request.form.get('condition')
        images = request.files.getlist('images[]')
        if not (title and description and category_name and price):
            flash('All fields except image are required.', 'danger')
            return render_template('/product/add_product.html', product=product, categories=categories, edit=True)
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            flash('Invalid category selected.', 'danger')
            return render_template('/product/add_product.html', product=product, categories=categories, edit=True)
        product.name = title
        product.description = description
        product.price = price
        product.condition = condition
        product.category_id = category.id
        # If a new image is uploaded, replace it
        if images and images[0].filename:
            image_file = images[0]
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'products')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            product.image_filename = filename
        db.session.commit()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('product.product_listing'))
    return render_template('/product/add_product.html', product=product, categories=categories, edit=True)




# product search
@product.route('/search', methods=['GET', 'POST'])
def product_search():
    from models.models import Product, Category
    products = []
    search_query = request.args.get('query', '')
    category_id = request.args.get('category_id', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    categories = Category.query.all()

    query = Product.query.filter(
        (Product.status == 'active') &
        (Product.is_deleted == False)
    )
    if search_query:
        query = query.filter(
            (Product.name.ilike(f'%{search_query}%')) |
            (Product.description.ilike(f'%{search_query}%'))
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    products = query.all()
    return render_template('/product/search.html', 
                          products=products, 
                          search_query=search_query,
                          categories=categories,
                          selected_category_id=category_id,
                          min_price=min_price,
                          max_price=max_price)



 


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


