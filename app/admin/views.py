from datetime import datetime
from app import db, admin, file_path
from app.models import AVAILABLE_MEASURE_TYPES, Food, User, MenuCategory
from flask import url_for
from flask_admin import form
from flask_admin.model import typefmt
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from flask_admin.contrib.sqla.filters import FilterEqual
from markupsafe import Markup
from datetime import date

def list_thumbnail(view, context, model, name):
    if not model.path:
        return ''
    return Markup('<img src="%s">' % url_for('static',
                                                 filename='food_images/'f'{form.thumbgen_filename(model.path)}'))

def date_format(view, value):
    return value.strftime("%d.%m.%Y")

MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
        date: date_format
    })

class UserView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
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

    column_type_formatters = MY_DEFAULT_FORMATTERS

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
        'path': list_thumbnail
    }

    form_excluded_columns = ('foods', 'slug')
    form_extra_fields = {
        'path': ImageUploadField('Изображение', base_path=file_path, thumbnail_size=(100, 100, True))
    }

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
        'path': list_thumbnail
    }

    form_excluded_columns = ('slug')
    form_choices = {
        'measure': AVAILABLE_MEASURE_TYPES
    }
    form_extra_fields = {
        'path': ImageUploadField('Изображение', base_path=file_path, thumbnail_size=(100, 100, True))
    }

admin.add_view(UserView(User, db.session))
admin.add_view(MenuCategoryView(MenuCategory, db.session))
admin.add_view(FoodView(Food, db.session))