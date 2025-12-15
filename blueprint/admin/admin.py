from sqlite3 import DatabaseError

from flask import Blueprint, render_template, redirect, flash, url_for
from extensions import db
from form.CategoryForm import CategoryForm
from models import Category

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
def _admin():
    return redirect('/admin/dashboard')


@admin_bp.route('/admin/dashboard')
def admin():
    return render_template('backend/admin/index.html')


@admin_bp.route('/admin/product')
def admin_product():
    return render_template('backend/admin/pages/product.html')


@admin_bp.route('/admin/category')
def admin_category():
    categories = Category.query.all()
    return render_template('backend/admin/pages/category/category.html', categories=categories)


@admin_bp.route('/admin/category/edit/<int:category_id>', methods=['GET', 'POST'])
def admin_category_edit(category_id):
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category.query.get_or_404(category_id)
        if category :
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
    return render_template('backend/admin/pages/category/edit.html', category=category, form=form , description=description , name=name , status=status)


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

    if form.validate_on_submit():
        category = Category(
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
