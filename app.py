import os
from datetime import timedelta

import click
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

import config
from blueprint.admin.admin import admin_bp
from blueprint.home import home_bp
from extensions import db
from flask_migrate import Migrate
from blueprint.admin.product.product import product_bp
from form.UserForm import LoginForm, RegisterForm
from models import User, Category
from upload_service import save_image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

migrate = Migrate(app, db)
db.init_app(app)

app.config.from_object('config')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.register_blueprint(home_bp)
app.register_blueprint(product_bp)
app.register_blueprint(admin_bp)
app.config['logo'] = 'static/admin/assets/images/logo-text-1.png'
app.config['title'] = 'Angkorkey'
app.config['icon'] = 'static/admin/assets/images/icon_logo.jpg'

app.config['SECRET_KEY'] = 'oythaiahleay168'
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["logo"] = "sql_logo.jpg"

import models

@app.before_request
def before_request():
    url = request.path
    if url.startswith('/admin/'):
        if not session.get('user_id'):
            flash('Please Login', 'danger')
            return redirect(url_for('login'))
    return None

@app.route('/upload')
def index():
    return render_template('upload.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        username_ = User.query.filter_by(username=username).first()
        if username_ and check_password_hash(username_.password, password):
            session.clear()
            session['user_id'] = username_.id
            session['username'] = username_.username
            flash(category="success", message="Login Successful")
            return redirect(url_for('admin.admin'))
        else:
            flash('Invalid username or password')
        return redirect(url_for('login'))
    return render_template('backend/auth/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        phone = form.phone.data
        password = generate_password_hash(form.password.data)
        user = User(username=username, phone=phone, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('backend/auth/register.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# for header categories info
@app.context_processor
def inject_categories():
    categories = Category.query.all()
    return dict(categories=categories)

# Define the command
@app.cli.command("create-admin")
@click.argument("name")
@click.argument("password")
def create_user(name, password):
    """Creates a new user. Usage: flask create-admin <name> <password>"""
    hashed_pw = generate_password_hash(password)

    # Check your User model to see if you need 'email' or 'phone' too!
    user = User(username=name, password=hashed_pw)

    db.session.add(user)
    db.session.commit()
    print(f"Successfully created user: {name}")


if __name__ == '__main__':
    app.run()

if __name__ == '__main__':
    app.run()
