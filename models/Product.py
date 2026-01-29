import math

from flask import request
from flask_paginate import get_page_parameter, Pagination
from sqlalchemy import text

from extensions import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=True)
    desc = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(5), nullable=False)
    images = db.relationship('ProductImage', backref='product', lazy=True)
    category_name = db.relationship('Category', backref='product', lazy=True)

    def __repr__(self):
        return f'Product {self.name}'


def getAllProduct():
    page = request.args.get(get_page_parameter(), default=1, type=int)
    per_page = 6
    offset_value = (page - 1) * per_page

    sql = text("""
               SELECT p.*, c.name as "category_name"
               FROM product p
                        INNER JOIN category c ON c.id = p.category_id LIMIT :limit
               OFFSET :offset
               """)

    results = db.session.execute(sql, {'limit': per_page, 'offset': offset_value}).fetchall()

    rows = text(
        """
        select COUNT(*)
        from product;
        """
    )
    _rows = db.session.execute(rows).fetchone()[0]

    pagination = Pagination(page=page, per_page=per_page, total=_rows, css_framework='bootstrap5')

    _results = {
        'list': results,
        'pagination': pagination,
    }

    return _results
