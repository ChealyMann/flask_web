import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from sqlalchemy import false
from werkzeug.utils import secure_filename

from form.ProductForm import ProductForm, ProductFormEdit, ProductImageAdd
from models import Product, ProductImage
from models.Product import getAllProduct  # <--- Import function ដែលយើងសរសេរពីមុន
from extensions import db
from Webp import save_picture

from upload_service import save_image

product_bp = Blueprint('product', __name__)


@product_bp.route('/admin/product')
def product():
    output = []
    products = getAllProduct()
    _products = Product.query.all()
    for _product in _products:
        output.append({
            'id': _product.id,
            'name': _product.name,
            'desc': _product.desc,
            'price': _product.price,
            'cost': _product.cost,
            'category_id': _product.category_id,
            'image': _product.image,
        })
    return render_template('backend/admin/pages/product/product.html', products=products, product=product,
                           _products=_products, output=output , os=os)


@product_bp.route('/admin/product/add', methods=['GET', 'POST'])
def product_add():
    form = ProductForm()
    if form.validate_on_submit():
        unique_filename = 'none.jpg'  # Default Image
        if form.image.data:
            unique_filename = save_image(form.image.data,
                                         current_app.config.get('UPLOAD_FOLDER'),
                                         current_app.config['ALLOWED_EXTENSIONS'])
        _product = Product(
            name=form.name.data,
            desc=form.desc.data,
            price=form.price.data,
            image=str(unique_filename),
            cost=form.cost.data,
            status=form.status.data,
            category_id=form.category.data.id,
        )
        db.session.add(_product)
        db.session.commit()

        flash('Product Added Successfully', 'success')
        return redirect(url_for('product.product'))

    return render_template('backend/admin/pages/product/add.html', form=form)


@product_bp.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def product_edit(product_id):
    _product = Product.query.get_or_404(product_id)
    form = ProductFormEdit()

    # Handle POST Request
    if form.validate_on_submit():
        _product.name = form.name.data
        _product.desc = form.desc.data
        _product.price = form.price.data
        _product.cost = form.cost.data
        _product.status = form.status.data
        _product.category_id = form.category.data.id

        if form.image.data:

            if _product.image and _product.image != 'none.jpg':
                old_file_path = os.path.join(current_app.root_path, 'static/images', _product.image)
                old_file_path_resized = os.path.join(current_app.root_path, 'static/images','resized_' + _product.image)
                old_file_path_thumb = os.path.join(current_app.root_path, 'static/images','thumb_' + _product.image)
                if os.path.exists(old_file_path or old_file_path_thumb or old_file_path_resized):
                    os.remove(old_file_path)
                    os.remove(old_file_path_resized)
                    os.remove(old_file_path_thumb)


            _product.image = save_image(form.image.data, current_app.config.get('UPLOAD_FOLDER'),
                                        current_app.config['ALLOWED_EXTENSIONS'])

        db.session.commit()
        flash('Product Updated Successfully', 'success')  # <--- ដូរ Message
        return redirect(url_for('product.product'))

    # Handle GET Request (Populate Form)
    if request.method == 'GET':
        form.name.data = _product.name
        form.desc.data = _product.desc
        form.price.data = _product.price
        form.cost.data = _product.cost
        form.status.data = _product.status
        form.category.data = _product.category_id  # Note: ត្រូវប្រាកដថា form field នេះទទួលយក ID

    return render_template('backend/admin/pages/product/edit.html', form=form, product=_product , os=os)


@product_bp.route('/admin/product/delete/<int:product_id>', methods=['POST'])
def product_delete(product_id):
    _product = Product.query.get_or_404(product_id)

    # ⚠️ Safe Delete Image Logic
    if _product.image and _product.image != 'none.jpg':
        file_path = os.path.join(current_app.root_path, 'static/images', _product.image)
        file_path_resized = os.path.join(current_app.root_path, 'static/images', 'resized_' + _product.image)
        file_path_thumb = os.path.join(current_app.root_path, 'static/images', 'thumb_' + _product.image)
        if os.path.exists(file_path or file_path_resized or file_path_thumb):
            try:
                os.remove(file_path)
                os.remove(file_path_resized)
                os.remove(file_path_thumb)
                print(f"Deleted image: {_product.image}")
            except Exception as e:
                print(f"Error deleting image: {e}")

    db.session.delete(_product)
    db.session.commit()
    flash('Product Deleted Successfully', 'success')
    return redirect(url_for('product.product'))


@product_bp.route('/admin/product/add_image/<int:product_id>', methods=['GET', 'POST'])
def product_add_image(product_id):
    form = ProductImageAdd()
    product_images = Product.query.get_or_404(product_id)
    if form.validate_on_submit():
        if not form.images.data:
            flash(message='No images added', category='error')
            return redirect(url_for('product.product_add_image', product_id=product_images.id))
        for file in form.images.data:
            unique_filename = save_picture(file)
            images_db = ProductImage(
                product_id=product_id,
                image=str(unique_filename)
            )
            db.session.add(images_db)
            db.session.commit()
        return redirect(url_for('product.product'))
    else:
        print(form.errors)

    return render_template('backend/admin/pages/product/add_images.html', form=form, product=product_images)
