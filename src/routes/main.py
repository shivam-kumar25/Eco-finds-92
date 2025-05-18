from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from src.models.product import Product
from src.models.category import Category

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=8)
    categories = Category.query.all()
    return render_template('index.html', title='Home', products=products, categories=categories)

@main.route('/about')
def about():
    return render_template('about.html', title='About')

@main.route('/user/dashboard')
@login_required
def user_dashboard():
    return render_template('user_dash.html', title='Dashboard')
