


from models.models import User, CartItem, Product
from flask_mail import Message, Mail
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from __init__ import db




payment = Blueprint('payment', __name__)

# Cart view
@payment.route('/cart', methods=['GET'])
def cart():
    from models.models import CartItem, Product
    
    if 'user_id' not in session:
        flash('Please login to view your cart', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get cart items for the logged-in user
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    
    # Calculate total price
    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity
    
    return render_template('payment/cart.html', 
                          cart_items=cart_items,
                          total=total,
                          title='Your Cart')

# Add to cart
@payment.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    from models.models import CartItem, Product
    
    if 'user_id' not in session:
        flash('Please login to add items to your cart', 'warning')
        return redirect(url_for('auth.login'))
    
    quantity = int(request.form.get('quantity', 1))
    
    # Check if the product exists
    product = Product.query.get_or_404(product_id)
    
    # Check if the product is already in the cart
    cart_item = CartItem.query.filter_by(
        user_id=session['user_id'], 
        product_id=product_id
    ).first()
    
    if cart_item:
        # Update quantity
        cart_item.quantity += quantity
    else:
        # Add new cart item
        cart_item = CartItem(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    flash(f'{product.name} added to your cart', 'success')
    return redirect(url_for('payment.cart'))

# Remove from cart
@payment.route('/remove-from-cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if 'user_id' not in session:
        flash('Please login to manage your cart', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get the cart item
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=session['user_id']
    ).first_or_404()
    
    # Delete the cart item
    db.session.delete(cart_item)
    db.session.commit()
    
    flash('Item removed from your cart', 'success')
    return redirect(url_for('payment.cart'))

# Update cart quantities
@payment.route('/update-cart', methods=['POST'])
def update_cart():
    if 'user_id' not in session:
        flash('Please login to manage your cart', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get all item IDs and quantities from the form
    items = request.form.to_dict()
    
    for key, value in items.items():
        if key.startswith('quantity_'):
            item_id = int(key.split('_')[1])
            quantity = int(value)
            
            if quantity > 0:
                # Update the cart item
                cart_item = CartItem.query.filter_by(
                    id=item_id,
                    user_id=session['user_id']
                ).first()
                
                if cart_item:
                    cart_item.quantity = quantity
    
    db.session.commit()
    flash('Cart updated successfully', 'success')
    return redirect(url_for('payment.cart'))

@payment.route('/payment', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please login to proceed with payment', 'warning')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        # Process the payment here (placeholder)
        # Clear the cart
        from models.models import CartItem
        CartItem.query.filter_by(user_id=session['user_id']).delete()
        db.session.commit()
        
        flash('Payment processed successfully!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('payment/payment_page.html', title='Payment')


