from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
admin = Admin()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    admin.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.profile import bp as profile_bp
    app.register_blueprint(profile_bp)

    from app.menu import bp as menu_bp
    app.register_blueprint(menu_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    return app

from app import admin, models

