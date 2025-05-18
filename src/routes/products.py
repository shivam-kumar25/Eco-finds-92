from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from src import db
from src.models.product import Product
from src.models.category import Category

products = Blueprint('products', __name__)

@products.route('/')
def all_products():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    
    if category_id:
        products_query = Product.query.filter_by(category_id=category_id)
        category = Category.query.get_or_404(category_id)
        title = f'Products in {category.name}'
    else:
        products_query = Product.query
        title = 'All Products'
    
    products_pagination = products_query.paginate(page=page, per_page=8)
    categories = Category.query.all()
    
    return render_template('products/index.html', 
                          title=title, 
                          products=products_pagination, 
                          categories=categories)

@products.route('/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('products/detail.html', title=product.name, product=product)

@products.route('/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        image_url = request.form.get('image_url')
        category_id = request.form.get('category_id')
        
        # Form validation
        if not all([name, description, price, category_id]):
            flash('Name, description, price and category are required', 'danger')
            categories = Category.query.all()
            return render_template('products/new.html', title='New Product', categories=categories)
        
        try:
            price = float(price)
        except ValueError:
            flash('Price must be a number', 'danger')
            categories = Category.query.all()
            return render_template('products/new.html', title='New Product', categories=categories)
        
        # Create new product
        product = Product(
            name=name,
            description=description,
            price=price,
            image_url=image_url,
            category_id=category_id,
            seller_id=current_user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product created successfully!', 'success')
        return redirect(url_for('products.product_detail', product_id=product.id))
    
    categories = Category.query.all()
    return render_template('products/new.html', title='New Product', categories=categories)

@products.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if the current user is the seller
    if product.seller_id != current_user.id:
        flash('You can only edit your own products', 'danger')
        return redirect(url_for('products.product_detail', product_id=product.id))
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.image_url = request.form.get('image_url')
        product.category_id = request.form.get('category_id')
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products.product_detail', product_id=product.id))
    
    categories = Category.query.all()
    return render_template('products/edit.html', title='Edit Product', product=product, categories=categories)

@products.route('/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if the current user is the seller
    if product.seller_id != current_user.id:
        flash('You can only delete your own products', 'danger')
        return redirect(url_for('products.product_detail', product_id=product.id))
    
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.all_products'))
