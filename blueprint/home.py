from flask import Blueprint, url_for, render_template, request

from models import Product, Category

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    products = Product.query.limit(4).all()
    return render_template('frontend/pages/index.html', products=products)

@home_bp.route('/product_detail{/<int:product_id>}')
def product_detail(product_id):
    product = Product.query.get(product_id)
    return render_template('frontend/pages/product-detail.html', product=product)


@home_bp.route('/cart')
def cart():
    return render_template('frontend/pages/cart.html')


@home_bp.route('/products')
def products():
    # 1. Capture Filters
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)
    is_ajax = request.args.get('ajax', type=int)

    # 2. Build Query
    query = Product.query

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))

    # 3. Execute
    products_list = query.all()

    # 4. AJAX RESPONSE: Return only the grid HTML
    if is_ajax:
        return render_template('frontend/layouts/product_grid.html', products=products_list)

    # 5. STANDARD RESPONSE: Return full page
    categories = Category.query.all()
    return render_template(
        'frontend/pages/products.html',
        products=products_list,
        categories=categories,
        current_category=category_id
    )