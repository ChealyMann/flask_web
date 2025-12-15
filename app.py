from flask import Flask
from blueprint.admin.admin import admin_bp
from blueprint.home import home_bp
from extensions import db
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

migrate = Migrate(app, db)
db.init_app(app)

app.register_blueprint(home_bp)
app.register_blueprint(admin_bp)
app.config['logo'] = 'static/admin/assets/images/logo-text-1.png'
app.config['title'] = 'Angkorkey'
app.config['icon'] = 'static/admin/assets/images/icon_logo.jpg'
app.config['SECRET_KEY'] = 'oythaiahleay168'

import models

if __name__ == '__main__':
    app.run()
