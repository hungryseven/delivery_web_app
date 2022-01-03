from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25))
    sex = db.Column(db.String(7))
    email = db.Column(db.String(120), index=True, unique=True)
    phone_number = db.Column(db.String(11), index=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'<User {self.first_name} {self.email}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class MenuCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_category = db.Column(db.String(20), unique=True)
    order = db.Column(db.Integer)
    path = db.Column(db.Unicode(128))

    def __repr__(self):
        return f'<Category {self.name_category}>'