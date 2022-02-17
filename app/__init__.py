import imp
import os
import os.path
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_breadcrumbs import Breadcrumbs
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig, ProductionConfig

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Авторизуйтесь для доступа к данной странице'
admin = Admin(template_mode='bootstrap4')
breadcrumbs = Breadcrumbs()
csrf = CSRFProtect()

images_path = os.path.join(os.path.dirname(__file__), 'static', 'food_images')
try:
    os.mkdir(images_path)
except OSError:
    pass

def create_app(config=ProductionConfig):
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

    if not app.debug and not app.testing:

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/delivery_app.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Delivery_app startup')

    return app

from app import models

