from app import db, admin, file_path
from app.models import AVAILABLE_MEASURE_TYPES, Food, User, MenuCategory
from flask import url_for
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from markupsafe import Markup

def list_thumbnail(view, context, model, name):
    if not model.path:
        return ''
    return Markup('<img src="%s">' % url_for('static',
                                                 filename=form.thumbgen_filename(model.path)))

class UserView(ModelView):
    column_labels = dict(first_name='Имя', phone_number='Номер телефона')
    column_exclude_list = ('password_hash', 'sex')
    column_searchable_list = ('email', 'phone_number')
    can_create = False
    can_edit = False
    can_delete = False

class MenuCategoryView(ModelView):
    column_labels = dict(name_category='Наименование категории', slug='URL адрес', order='Приоритет', path='Изображение')
    column_editable_list = ('name_category', 'slug', 'order')
    column_default_sort = 'order'
    form_excluded_columns = ('foods', 'slug')

    column_formatters = {
        'path': list_thumbnail
    }

    form_extra_fields = {
        'path': ImageUploadField('Изображение', base_path=file_path, thumbnail_size=(100, 100, True))
    }

class FoodView(ModelView):
    column_labels = dict(
        name_food='Наименование позиции',
        description='Описание/Ингредиенты',
        weight='Вес/Объем',
        measure='Единица измерения',
        price='Цена',
        path='Изображение',
        category='Категория'
        )

    form_choices = {
        'measure': AVAILABLE_MEASURE_TYPES
    }

    column_formatters = {
        'path': list_thumbnail
    }

    form_extra_fields = {
        'path': ImageUploadField('Изображение', base_path=file_path, thumbnail_size=(100, 100, True))
    }

admin.add_view(UserView(User, db.session))
admin.add_view(MenuCategoryView(MenuCategory, db.session))
admin.add_view(FoodView(Food, db.session))