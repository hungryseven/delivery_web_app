from flask import redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required
from app import db
from app.models import Address, Food
from app.profile import bp
from app.profile.forms import InfoForm, PasswordForm, AddressForm

# TODO: Во многих представлениях используются обычные редиректы,
# вместо которых лучше использовать AJAX. По мере изучения JS
# добавлять скрипты.

# Функция-представление страницы профиля с персональными данными
@bp.route('/info', methods=['GET', 'POST'])
@login_required
def info():
    info_form = InfoForm()
    password_form = PasswordForm()
    # Так как на странице 2 формы, то проверяем событие нажатия
    # и валидацию в отдельных условиях
    if info_form.submit_info.data and info_form.validate():
        current_user.sex = info_form.sex.data
        current_user.first_name = info_form.first_name.data
        current_user.email = info_form.email.data
        db.session.commit()
        flash('Данные успешно сохранены')
        return redirect(url_for('profile.info'))
    if password_form.submit_password.data and password_form.validate():
        if not current_user.check_password(password_form.current_password.data):
            flash('Неверный пароль')
            return redirect(url_for('profile.info'))
        current_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('Пароль успешно изменен')
        return redirect(url_for('profile.info'))
    return render_template('profile/info.html', title='Персональные данные', info_form=info_form, password_form=password_form)

# Функция-представление страницы профиля с адресами доставки
@bp.route('/address', methods=['GET', 'POST'])
@login_required
def address():
    address_form = AddressForm()
    # Так как на странице 3 события формы (добавление, редактирование, удаление),
    # то проверяем нажатие каждого и валидацию (кроме удаления) в отдельных условиях
    if address_form.submit_address.data and address_form.validate():
        address_to_add = Address(
            street=address_form.street.data,
            house=address_form.house.data,
            building=address_form.building.data,
            entrance=address_form.entrance.data,
            floor=address_form.floor.data,
            apartment=address_form.apartment.data,
            additional_info=address_form.additional_info.data, 
            user=current_user)
        db.session.add(address_to_add)
        db.session.commit()
        flash('Адрес доставки успешно сохранен')
        return redirect(url_for('profile.address'))
    if address_form.edit_address.data and address_form.validate():
        address_to_edit = Address.query.get(address_form.address_id.data)
        address_to_edit.street = address_form.street.data
        address_to_edit.house = address_form.house.data
        address_to_edit.building = address_form.building.data
        address_to_edit.entrance = address_form.entrance.data
        address_to_edit.floor = address_form.floor.data
        address_to_edit.apartment = address_form.apartment.data
        address_to_edit.additional_info = address_form.additional_info.data
        db.session.commit()
        flash('Адрес доставки успешно изменен')
        return redirect(url_for('profile.address'))
    if address_form.delete_address.data:
        address_to_delete = Address.query.get(address_form.address_id.data)
        db.session.delete(address_to_delete)
        db.session.commit()
        flash('Адрес доставки успешно удален')
        return redirect(url_for('profile.address'))
    return render_template('profile/address.html', title='Адрес доставки', address_form=address_form)

# Функция-представление страницы профиля с избранными позициями
@bp.route('/favourites')
@login_required
def favourites():
    favs = current_user.favs
    return render_template('profile/favourites.html', title='Избранное', favs=favs)

@bp.route('/favourites/add/<food_id>')
@login_required
def add_to_favourites(food_id):
    food = Food.query.get(food_id)
    current_user.favs.append(food)
    db.session.commit()
    next_page = request.args.get('next')
    print(next_page)
    return redirect(next_page)

@bp.route('/favourites/delete/<food_id>')
@login_required
def delete_from_favourites(food_id):
    food = Food.query.get(food_id)
    current_user.favs.remove(food)
    db.session.commit()
    next_page = request.args.get('next')
    return redirect(next_page)

# Функция-представление страницы профиля историей заказов
@bp.route('/profile/orders')
@login_required
def orders():
    return render_template('profile/orders.html', title='История заказов')