import os
from sqlite3 import DatabaseError

from flask import Blueprint, render_template, redirect, flash, url_for, request, session, current_app
from sqlalchemy import false
from werkzeug.utils import secure_filename

from Webp import save_picture
from extensions import db
from form.CategoryForm import CategoryForm
from form.UserForm import UserForm, UserFormEdit
from models import Category, User
from werkzeug.security import generate_password_hash, check_password_hash

from upload_service import save_image

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
def _admin():
    return redirect('/admin/dashboard')


@admin_bp.route('/admin/dashboard')
def admin():
    return render_template('backend/admin/index.html')


@admin_bp.route('/admin/category')
def admin_category():
    categories = Category.query.all()
    return render_template('backend/admin/pages/category/category.html', categories=categories)


@admin_bp.route('/admin/category/edit/<int:category_id>', methods=['GET', 'POST'])
def admin_category_edit(category_id):
    form = CategoryForm()
    if form.validate_on_submit():

        category = Category.query.get_or_404(category_id)

        if form.image.data:

            if category.image and category.image != 'none.jpg':
                old_file_path = os.path.join(current_app.root_path, 'static/images', category.image)
                old_file_path_resized = os.path.join(current_app.root_path, 'static/images',
                                                     'resized_' + category.image)
                old_file_path_thumb = os.path.join(current_app.root_path, 'static/images', 'thumb_' + category.image)
                if os.path.exists(old_file_path or old_file_path_thumb or old_file_path_resized):
                    os.remove(old_file_path)
                    os.remove(old_file_path_resized)
                    os.remove(old_file_path_thumb)

            category.image = save_image(form.image.data, current_app.config.get('UPLOAD_FOLDER'),
                                        current_app.config['ALLOWED_EXTENSIONS'])

        if category:
            category.image = category.image
            category.name = form.name.data.strip()
            category.desc = form.desc.data.strip()
            category.status = form.status.data.strip()
            db.session.commit()
            db.session.close()
            flash('Category has been updated successfully!', 'success')
            return redirect(url_for('admin.admin_category'))
    category = Category.query.get_or_404(category_id)
    description = form.desc.data = category.desc
    name = form.name.data = category.name
    status = form.status.data = category.status
    return render_template('backend/admin/pages/category/edit.html', category=category, form=form,
                           description=description, name=name, status=status,os=os)


@admin_bp.route('/admin/category/delete/<int:category_id>', methods=['POST'])
def admin_category_delete(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        flash('Category has been deleted successfully!', 'success')
        return redirect('/admin/category')
    except(ValueError, TypeError, Exception, DatabaseError):
        db.session.rollback()
        print(Exception, TypeError, ValueError, DatabaseError)
        return redirect('/admin/category')


@admin_bp.route('/admin/category/add', methods=['GET', 'POST'])
def admin_category_add():
    form = CategoryForm()
    filename = ""
    if form.validate_on_submit():
        if form.image.data:
            filename = save_image(form.image.data, current_app.config['UPLOAD_FOLDER'],
                                  current_app.config['ALLOWED_EXTENSIONS'])
        category = Category(
            image=str(filename),
            name=form.name.data,
            desc=form.desc.data,
            status=form.status.data

        )
        db.session.add(category)
        db.session.commit()
        db.session.close()
        flash('Category has been added successfully!', 'success')
        return redirect(url_for('admin.admin_category'))

    return render_template(
        'backend/admin/pages/category/add.html', form=form)


@admin_bp.route('/admin/user')
def admin_user():
    users = User.query.all()
    return render_template('backend/admin/pages/user/user.html', users=users)


@admin_bp.route('/admin/user/add', methods=['GET', 'POST'])
def admin_user_add():
    form = UserForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data)

        )
        db.session.add(user)
        db.session.commit()
        db.session.close()
        flash('User has been added successfully!', 'success')
        return redirect(url_for('admin.admin_user'))

    return render_template(
        'backend/admin/pages/user/add.html', form=form)


@admin_bp.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
def admin_user_edit(user_id):
    form = UserFormEdit()
    if form.validate_on_submit():
        user = User.query.get_or_404(user_id)
        if user:
            user.username = form.username.data.strip()
            user.password = generate_password_hash(form.password.data.strip())
            db.session.commit()
            db.session.close()
            flash('User has been updated successfully!', 'success')
            return redirect(url_for('admin.admin_user'))
    user = User.query.get_or_404(user_id)
    password = form.password.data = user.password
    username = form.username.data = user.username
    return render_template('backend/admin/pages/user/edit.html', user=user, form=form,
                           username=username, password=password)


@admin_bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
def admin_user_delete(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted successfully!', 'success')
        return redirect('/admin/user')
    except(ValueError, TypeError, Exception, DatabaseError):
        db.session.rollback()
        print(Exception, TypeError, ValueError, DatabaseError)
        return redirect('/admin/user')
