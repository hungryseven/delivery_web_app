import os
import os.path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_breadcrumbs import Breadcrumbs
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Авторизуйтесь для доступа к данной странице'
admin = Admin(template_mode='bootstrap4')
breadcrumbs = Breadcrumbs()
csrf = CSRFProtect()

images_path = os.path.join(os.path.dirname('/app/static/food_images'), 'food_images')
try:
    os.mkdir(images_path)
except OSError:
    pass

def create_app(config=Config):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login.init_app(app)
    admin.init_app(app)
    breadcrumbs.init_app(app)
    csrf.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.profile import bp as profile_bp
    app.register_blueprint(profile_bp, url_prefix='/profile')

    from app.menu import bp as menu_bp
    app.register_blueprint(menu_bp, url_prefix='/menu')
    
    from app.cart import bp as cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app

from app import models

