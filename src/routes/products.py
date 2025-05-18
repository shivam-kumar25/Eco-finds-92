from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from src import db
import os
import uuid
from werkzeug.utils import secure_filename
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
    # Only allow admins to create products
    if not current_user.is_admin:
        flash('Only administrators can add products', 'danger')
        return redirect(url_for('products.all_products'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        image = request.files.get('image')
        
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
        
        # Handle image upload
        image_filename = None
        if image and image.filename:
            # Secure the filename and create a unique name
            filename = secure_filename(image.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            # Save file to uploads folder
            upload_path = os.path.join(current_app.root_path, 'static', 'uploads', unique_filename)
            image.save(upload_path)
            image_filename = unique_filename
        
        # Get additional fields
        condition = request.form.get('condition', 'Used - Good')
        original_packaging = 'original_packaging' in request.form
        eco_impact_score = int(request.form.get('eco_impact_score', 3))
        estimated_co2_saved = float(request.form.get('estimated_co2_saved', 0.0))
        
        # Create new product
        product = Product(
            name=name,
            description=description,
            price=price,
            image_filename=image_filename,
            category_id=category_id,
            seller_id=current_user.id,
            condition=condition,
            original_packaging=original_packaging,
            eco_impact_score=eco_impact_score,
            estimated_co2_saved=estimated_co2_saved
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product created successfully!', 'success')
        return redirect(url_for('products.all_products'))
    
    categories = Category.query.all()
    return render_template('products/new.html', title='New Product', categories=categories)

@products.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    # Only allow admins to edit products
    if not current_user.is_admin:
        flash('Only administrators can edit products', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))
        
    product = Product.query.get_or_404(product_id)    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.category_id = request.form.get('category_id')
        product.condition = request.form.get('condition', 'Used - Good')
        product.original_packaging = 'original_packaging' in request.form
        
        # Handle image upload
        image = request.files.get('image')
        if image and image.filename:
            # Delete old image if it exists
            if product.image_filename:
                old_image_path = os.path.join(current_app.root_path, 'static', 'uploads', product.image_filename)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
                    
            # Save new image
            filename = secure_filename(image.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            upload_path = os.path.join(current_app.root_path, 'static', 'uploads', unique_filename)
            image.save(upload_path)
            product.image_filename = unique_filename
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products.product_detail', product_id=product.id))
    
    categories = Category.query.all()
    return render_template('products/edit.html', title='Edit Product', product=product, categories=categories)

@products.route('/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    # Only allow admins to delete products
    if not current_user.is_admin:
        flash('Only administrators can delete products', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))
        
    product = Product.query.get_or_404(product_id)
    
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.all_products'))
