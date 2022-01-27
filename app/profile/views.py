from flask import jsonify, redirect, url_for, render_template, flash, request, session
from flask_login import current_user, login_required
from app import db
from app.models import Address, Food
from app.profile import bp as profile_bp
from app.profile.forms import InfoForm, PasswordForm, AddressForm
from app.auth.phone_verification import request_verification_token, parse_phone_number

# TODO: Во многих представлениях используются обычные редиректы,
# вместо которых лучше использовать AJAX. По мере изучения JS
# добавлять скрипты.

# Функция-представление страницы профиля с персональными данными
@profile_bp.route('/info', methods=['GET', 'POST'])
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

# Функция-представление восстановления пароля внутри профиля.
# Параметр 'prev' необходим для возврата на страницу профиля
# после восстановления пароля
@profile_bp.route('/reset_password')
@login_required
def reset_password():
    phone_number = '+7' + current_user.phone_number
    session['phone_number'] = phone_number
    request_verification_token(phone_number)
    return redirect(url_for('auth.verify', next='reset_password_verify', prev=url_for('profile.info')))

# Функция-представление страницы профиля с адресами доставки
@profile_bp.route('/address', methods=['GET', 'POST'])
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
@profile_bp.route('/favourites')
@login_required
def favourites():
    favs = current_user.favs
    return render_template('profile/favourites.html', title='Избранное', favs=favs)

# Функция-представление добавления позиции/товара в избранное.
# Если товара с таким id не существует, то выкинет 404 ошибку.
# Если товар УЖЕ находится в избранном и его пытаются добавить, то вернет JSON с ошибкой
@profile_bp.route('/favourites/add')
@login_required
def add_to_favourites():
    food_id = request.args.get('id')
    food = Food.query.get_or_404(food_id)
    if food in current_user.favs:
        return jsonify({'id': food.id, 'result': 'error'})
    current_user.favs.append(food)
    db.session.commit()
    return jsonify({'id': food.id, 'result': 'success'})

# Функция-представление удаления позиции/товара из избранного.
# Если товара с таким id не существует, то выкинет 404 ошибку.
# Если товара НЕТ в избранном и его пытаются удалить, то вернет JSON с ошибкой
@profile_bp.route('/favourites/delete')
@login_required
def delete_from_favourites():
    food_id = request.args.get('id')
    food = Food.query.get_or_404(food_id)
    if food not in current_user.favs:
        return jsonify({'id': food.id, 'result': 'error'})
    current_user.favs.remove(food)
    db.session.commit()
    return jsonify({'id': food.id, 'result': 'success'})

# Функция-представление, возвращающая JSON с id товаров/позиций,
# которые есть в избранном у пользователя
@profile_bp.route('/favourites/api')
@login_required
def get_user_favourites():
    user_favourites = [food.id for food in current_user.favs]
    return jsonify(user_favourites)

# Функция-представление страницы профиля историей заказов
@profile_bp.route('/profile/orders')
@login_required
def orders():
    return render_template('profile/orders.html', title='История заказов')