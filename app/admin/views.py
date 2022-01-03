from app import db, admin, file_path
from app.models import User, MenuCategory
from flask import url_for
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from markupsafe import Markup

class UserView(ModelView):
    column_exclude_list = ('password_hash')
    column_searchable_list = ('email', 'phone_number')
    can_create = False
    can_edit = False
    can_delete = False

class MenuCategoryView(ModelView):
    column_editable_list = ('name_category', 'order')

    def list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup('<img src="%s">' % url_for('static',
                                                 filename=form.thumbgen_filename(model.path)))

    column_formatters = {
        'path': list_thumbnail
    }


    form_extra_fields = {
        'path': ImageUploadField('Image', base_path=file_path, thumbnail_size=(100, 100, True))
    }

admin.add_view(UserView(User, db.session))
admin.add_view(MenuCategoryView(MenuCategory, db.session))