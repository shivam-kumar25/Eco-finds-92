from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from src import db
from src.models.cart import CartItem
from src.models.order import Order, OrderItem

orders = Blueprint('orders', __name__)

@orders.route('/')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('orders/history.html', title='Order History', orders=orders)

@orders.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Ensure the order belongs to the current user
    if order.user_id != current_user.id:
        flash('You can only view your own orders', 'danger')
        return redirect(url_for('orders.order_history'))
    
    return render_template('orders/detail.html', title=f'Order #{order.id}', order=order)

@orders.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    # Ensure there are items in the cart
    if not cart_items:
        flash('Your cart is empty', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    # Calculate the total amount
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        # Create a new order
        order = Order(user_id=current_user.id, total_amount=total_amount)
        db.session.add(order)
        
        # Create order items from cart items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
        
        # Clear the cart
        for cart_item in cart_items:
            db.session.delete(cart_item)
        
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('orders.order_detail', order_id=order.id))
    
    return render_template('orders/checkout.html', title='Checkout', cart_items=cart_items, total=total_amount)
