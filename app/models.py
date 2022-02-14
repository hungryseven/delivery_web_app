from email.policy import default
from app import db, login
from flask_login import UserMixin
from flask_sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
from datetime import datetime

# Миксин класс моделей БД
class ModelMixin():

    # Метод для события, который создает/обновляет
    # значение поля 'slug' при создании/обновлении экземпляра класса MenuCategory/Food
    # на основе значения поля 'name_category'/'name_food'
    @staticmethod
    def slugify(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)

    # Метод для события, которыq обновляет значение поля 'end_order' модели Order
    # если значение поля 'order_status' устанавливает в 'Доставлен' или 'Отменен'
    @staticmethod
    def set_end_order_datetime(target, value, oldvalue, initiator):
        if value == 'Доставлен' or value == 'Отменен' and value != oldvalue:
            target.end_order = datetime.utcnow()


# Ассоциативная таблица "избранное" для отношения многие-ко-многим для таблиц User и Food.
# Предоставляет информацию о том, какие товары находятся в избранном у пользователей
user_food = db.Table('user_food',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True)
)

# Ассоциативная таблица для отношения многие-ко-многим для таблиц Order и Food.
# Предоставляет информацию о том, какие товары были в каждом заказе и в каком количестве
class OrderFood(db.Model):
    order_id = db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True)
    food_id = db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True)
    food_quantity = db.Column(db.Integer)
    food = db.relationship('Food', back_populates='orders')
    order = db.relationship('Order', back_populates='foods')

# Модель с данными основными данными о пользователях
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25))
    sex = db.Column(db.String(7))
    email = db.Column(db.String(120), index=True)
    phone_number = db.Column(db.String(10), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    registration_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    addresses = db.relationship('Address', backref='user', lazy='dynamic')
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    favs = db.relationship('Food', secondary=user_food, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'{self.first_name}'

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
        return f'Ул. {self.street}, {self.house}{self.building}'

# Модель с данными о категориях еды/товаров
class MenuCategory(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_category = db.Column(db.String(20), unique=True, nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    order = db.Column(db.Integer)
    path = db.Column(db.Unicode(128))
    foods = db.relationship('Food', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'{self.name_category}'

# Функция-регистратор события 
event.listen(MenuCategory.name_category, 'set', MenuCategory.slugify, retval=False)

AVAILABLE_MEASURE_TYPES = [(u'г', u'г'), (u'кг', u'кг'), (u'мл', u'мл'), (u'л', u'л')]

# Модель с данными о каждой позиции еды/товара
class Food(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_food = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255))
    weight = db.Column(db.Integer, nullable=False)
    measure = db.Column(db.String(2), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    path = db.Column(db.Unicode(128))
    category_id = db.Column(db.Integer, db.ForeignKey('menu_category.id'), nullable=False)
    orders = db.relationship('OrderFood', back_populates='food')

    def __repr__(self):
        return f'{self.name_food}'

# Функция-регистратор события 
event.listen(Food.name_food, 'set', Food.slugify, retval=False)

AVAILABLE_ORDER_STATUSES = [
    (u'Принят', u'Принят'),
    (u'Готовится', u'Готовится'),
    (u'В процессе доставки', u'В процессе доставки'),
    (u'Доставлен', u'Доставлен'),
    (u'Отменен', u'Отменен')
]

# Модель с данными о заказах
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25))
    phone_number = db.Column(db.String(10), index=True)
    address = db.Column(db.String(512))
    start_order = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    delivery_datetime = db.Column(db.DateTime, index=True)
    payment_method = db.Column(db.String(20))
    total_price = db.Column(db.Integer)
    persons = db.Column(db.Integer)
    order_notes = db.Column(db.String(256))
    end_order = db.Column(db.DateTime, index=True)
    order_status = db.Column(db.String(25), default='В обработке')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    foods = db.relationship('OrderFood', back_populates='order')

    def __repr__(self):
        return f'Заказ №{self.id}'

# Функция-регистратор события 
event.listen(Order.order_status, 'set', MenuCategory.set_end_order_datetime, retval=False)