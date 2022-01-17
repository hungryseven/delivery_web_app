from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import event
from slugify import slugify

# Миксин класс, содержащий метод для события, который создает/обновляет
# значение поля 'slug' при создании/обновлении экземпляра класса MenuCategory/Food
# на основе значения поля 'name_category'/'name_food'
class SlugMixin():

    @staticmethod
    def slugify(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)

# Вспомогательная таблица "избранное" для отношения многие-ко-многим
# для таблиц User и Food 
user_food = db.Table('user_food',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True)
)
# Модель с данными основными данными о пользователях
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25))
    sex = db.Column(db.String(7))
    email = db.Column(db.String(120), index=True, unique=True)
    phone_number = db.Column(db.String(11), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    addresses = db.relationship('Address', backref='user', lazy='dynamic')
    favs = db.relationship('Food', secondary=user_food, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'Пользователь {self.first_name} {self.phone_number}'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Модель с данными об адресах пользователей
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(128))
    house = db.Column(db.String(10))
    building = db.Column(db.String(50))
    entrance = db.Column(db.String(3))
    floor = db.Column(db.String(3))
    apartment = db.Column(db.String(5))
    additional_info = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'Улица {self.street}, {self.house}{self.building}'

# Модель с данными о категориях еды/товаров
class MenuCategory(SlugMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_category = db.Column(db.String(20), unique=True)
    slug = db.Column(db.String(255), unique=True)
    order = db.Column(db.Integer)
    path = db.Column(db.Unicode(128))
    foods = db.relationship('Food', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'{self.name_category}'

# Функция-регистратор события 
event.listen(MenuCategory.name_category, 'set', MenuCategory.slugify, retval=False)

AVAILABLE_MEASURE_TYPES = [(u'г', u'г'), (u'кг', u'кг'), (u'мл', u'мл'), (u'л', u'л')]

# Модель с данными о каждой позиции еды/товара
class Food(SlugMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_food = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))
    weight = db.Column(db.Integer, nullable=False)
    measure = db.Column(db.String(2), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    path = db.Column(db.Unicode(128))
    category_id = db.Column(db.Integer, db.ForeignKey('menu_category.id'), nullable=False)

    def __repr__(self):
        return f'{self.name_food}'

# Функция-регистратор события 
event.listen(Food.name_food, 'set', Food.slugify, retval=False)
