from app import db, admin, images_path
from app.models import AVAILABLE_MEASURE_TYPES, AVAILABLE_ORDER_STATUSES, User, MenuCategory, Food, Order
from flask import url_for, Markup
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from flask_admin.contrib.sqla.filters import FilterEqual
from wtforms import DateTimeField
from datetime import timezone

# Функция форматирует колонки с путем изображения, заменяя его на плитку с изображением
def _list_thumbnail(view, context, model, name):
    if not model.path:
        return ''
    return Markup('<img src="%s">' % url_for('static',
                                                 filename='food_images/'f'{form.thumbgen_filename(model.path)}'))

# Функция форматирует колонки с объектами класса datetime из UTC в локальное время                                              
def _datetime_formatter(view, context, model, name):
        value = getattr(model, name, '')
        if value:
            return value.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%d.%m.%y в %H:%M')
        return ''

# ModelView для модели User
class UserView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    column_details_exclude_list = ('password_hash')
    column_labels = dict(
        first_name='Имя',
        phone_number='Номер телефона',
        sex='Пол',
        registration_date='Дата регистрации'
    )
    column_filters = (
        'phone_number',
        'email'
    )
    column_exclude_list = ('password_hash')
    column_searchable_list = ('email', 'phone_number')
    column_formatters = {
        'registration_date': _datetime_formatter
    }

    # По умолчанию Flask-admin читает все объекты как StringField
    # переписываем колонки с датами в DateTimeField
    form_overrides = dict(registration_date=DateTimeField)

# ModelView для модели MenuCategory
class MenuCategoryView(ModelView):
    column_labels = dict(
        name_category='Наименование категории',
        slug='URL адрес',
        order='Приоритет',
        path='Изображение'
    )
    column_editable_list = ('name_category', 'slug', 'order')
    column_default_sort = 'order'
    column_formatters = {
        'path': _list_thumbnail
    }

    form_excluded_columns = ('foods', 'slug')

    # Добавляет в форму дополнительную колонку для загрузки изображения
    form_extra_fields = {
        'path': ImageUploadField('Изображение', base_path=images_path, thumbnail_size=(100, 100, True))
    }

# ModelView для модели Food
class FoodView(ModelView):
    can_view_details = True
    column_labels = dict(
        name_food='Наименование позиции',
        slug='URL адрес',
        description='Описание/Ингредиенты',
        weight='Вес/Объем',
        measure='Единица измерения',
        price='Цена',
        path='Изображение',
        category='Категория'
    )
    column_editable_list = (
        'name_food',
        'slug',
        'description',
        'weight',
        'measure',
        'price',
        'category'
    )
    column_searchable_list = (
        'name_food',
    )
    column_default_sort = [('category_id', False), ('name_food', False)]
    column_filters = (
        'name_food',
        'description',
        FilterEqual(column=MenuCategory.name_category, name='Категория')
    )
    column_formatters = {
        'path': _list_thumbnail
    }

    form_excluded_columns = ('slug', 'orders', 'users')
    form_choices = {
        'measure': AVAILABLE_MEASURE_TYPES
    }

    # Добавляет в форму дополнительную колонку для загрузки изображения
    form_extra_fields = {
        'path': ImageUploadField('Изображение', base_path=images_path, thumbnail_size=(100, 100, True))
    }

# ModelView для модели Order
class OrderView(ModelView):

    # Функция форматирует колонку 'user', добавляя ссылку для перехода в detail_view модели UserView
    def _user_link_formatter(view, context, model, name):
        field = getattr(model, name, '')
        if field:
            url = url_for('user.details_view', id=field.id)
            return Markup(f'<a href="{url}">{field}</a>')
        return 'Анонимный пользователь'

    # Функция форматирует колонку 'foods'. Экземпляры класса OrderFood форматируются
    # в наименования позиций (с ссылками на detail_view модели FoodView) и их количество
    # для корректного отображения состава заказа
    def _order_foods_formatter(view, context, model, name):
        foods = getattr(model, name)
        food_list = ''
        for food in foods:
            food_inst = Food.query.get(food.food_id)
            url = url_for('food.details_view', id=food_inst.id)
            food_list += Markup(f'<p>{food.food_quantity} x <a href="{url}">{food_inst.name_food}</a></p>')
        return food_list
   
    can_create = False
    can_delete = False
    can_edit = False
    can_view_details = True

    column_display_pk = True
    column_labels = dict(
        id='Номер заказа',
        first_name='Имя',
        phone_number='Номер телефона',
        address='Адрес доставки',
        start_order='Время оформления',
        delivery_datetime='Доставить к',
        payment_method='Способ оплаты',
        total_price='Сумма заказа',
        persons='Количество персон',
        order_notes='Примечания',
        end_order='Время окончания',
        order_status='Статус заказа',
        foods='Состав заказа',
        user='Пользователь'
    )
    column_editable_list = (
        'order_status',
    )
    column_list = ('id', 'first_name', 'phone_number', 'address', 'start_order',
                    'delivery_datetime', 'total_price', 'order_status', 'user')
    column_details_list = ('id', 'first_name', 'phone_number', 'address', 'start_order', 'delivery_datetime', 'payment_method',
                            'total_price', 'persons', 'order_notes', 'end_order', 'order_status', 'foods', 'user')
    column_searchable_list = (
        'id', 'phone_number', 'order_status', 'address', 'payment_method'
    )
    column_filters = (
        'address',
        'start_order',
        'delivery_datetime',
        'end_order',
        'total_price',
        'order_status'
    )
    column_default_sort = [('start_order', False), ('delivery_datetime', False)]            
    column_formatters = {
        'start_order': _datetime_formatter,
        'delivery_datetime': _datetime_formatter,
        'end_order': _datetime_formatter,
        'user': _user_link_formatter,
        'foods': _order_foods_formatter
    }

    # По умолчанию Flask-admin читает все объекты как StringField
    # переписываем колонки с датами в DateTimeField
    form_overrides = dict(start_order=DateTimeField, delivery_datetime=DateTimeField, end_order=DateTimeField)

    form_choices = {
            'order_status': AVAILABLE_ORDER_STATUSES
        }

admin.add_view(UserView(User, db.session))
admin.add_view(MenuCategoryView(MenuCategory, db.session))
admin.add_view(FoodView(Food, db.session))
admin.add_view(OrderView(Order, db.session))