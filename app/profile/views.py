from time import strftime
from flask import jsonify, redirect, url_for, render_template, flash, request, session
from flask_login import current_user, login_required
from app import db
from app.models import Address, Food
from app.profile import bp as profile_bp
from app.profile.forms import InfoForm, PasswordForm, AddressForm
from app.auth.phone_verification import request_verification_token
from datetime import timezone, datetime

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
        flash('Данные успешно сохранены', category='alert alert-success')
        return redirect(url_for('profile.info'))
    if password_form.submit_password.data and password_form.validate():
        if not current_user.check_password(password_form.current_password.data):
            flash('Неверный пароль', category='alert alert-danger')
            return redirect(url_for('profile.info'))
        current_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('Пароль успешно изменен', category='alert alert-success')
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
@profile_bp.route('/address')
@login_required
def address():
    address_form = AddressForm()
    return render_template('profile/address.html', title='Адрес доставки', address_form=address_form)

# Функция-представление добавления адреса
@profile_bp.route('/address/add', methods=['POST'])
@login_required
def add_address():
    address_form = AddressForm()
    if address_form.validate_on_submit():
        address_to_add = Address(
            street=request.form.get('street'),
            house=request.form.get('house'),
            building=request.form.get('building', ''),
            entrance=request.form.get('entrance', ''),
            floor=request.form.get('floor', ''),
            apartment=request.form.get('apartment', ''),
            additional_info=request.form.get('additional_info', ''), 
            user_id=current_user.id
        )
        db.session.add(address_to_add)
        db.session.commit()
        flash('Адрес доставки успешно сохранен', category='alert alert-success')

        # Возвращаем адрес с текущей страницей, чтобы на нее перейти при успешном запросе
        return jsonify({'result': 'success', 'address_page': url_for('profile.address')})

    # Возвращаем ошибки валидации полей формы
    return jsonify({'result': 'error', 'errors': address_form.errors})

# Функция-представление редактирования уже добавленного адреса
@profile_bp.route('/address/edit', methods=['POST'])
@login_required
def edit_address():
    address_form = AddressForm()
    address_id = request.form.get('address_id')
    address_to_edit = Address.query.get_or_404(address_id)

    # Если редактируемый адрес не принадлежит юзеру, то вернет JSON с ошибкой
    if address_to_edit not in current_user.addresses:
        return jsonify({'result': 'error'})

    if address_form.validate_on_submit():
        address_to_edit.street = request.form.get('street')
        address_to_edit.house = request.form.get('house')
        address_to_edit.building = request.form.get('building', '')
        address_to_edit.entrance = request.form.get('entrance', '')
        address_to_edit.floor = request.form.get('floor', '')
        address_to_edit.apartment = request.form.get('apartment', '')
        address_to_edit.additional_info = request.form.get('additional_info', '')
        db.session.commit()
        flash('Адрес доставки успешно изменен', category='alert alert-success')

        # Возвращаем адрес с текущей страницей, чтобы на нее перейти при успешном запросе
        return jsonify({'result': 'success', 'address_page': url_for('profile.address')})

    # Возвращаем ошибки валидации полей формы
    return jsonify({'result': 'error', 'errors': address_form.errors})

# Функция-представление удаления сохраненного адреса
@profile_bp.route('/address/delete', methods=['POST'])
@login_required
def delete_address():
    address_id = request.form.get('id')
    address_to_delete = Address.query.get_or_404(address_id)

    # Если удаляемый адрес не принадлежит юзеру, то вернет JSON с ошибкой
    if address_to_delete not in current_user.addresses:
        return jsonify({'result': 'error'})

    db.session.delete(address_to_delete)
    db.session.commit()
    return jsonify(
        {
            'result': 'success', 
            'flashed': {'text': 'Адрес доставки успешно удален', 'category': 'alert alert-success'}
        }
    )

# Функция-представление страницы профиля с избранными позициями
@profile_bp.route('/favourites')
@login_required
def favourites():
    favs = current_user.favs
    return render_template('profile/favourites.html', title='Избранное', favs=favs)

# Функция-представление добавления позиции/товара в избранное.
@profile_bp.route('/favourites/add', methods=['POST'])
def add_to_favourites():
    if current_user.is_authenticated:
        food_id = request.form.get('id')
        food = Food.query.get_or_404(food_id)

        # Если товар УЖЕ находится в избранном и его пытаются добавить, то вернет JSON с ошибкой
        if food in current_user.favs:
            return jsonify({'result': 'error', 'id': food.id})

        current_user.favs.append(food)
        db.session.commit()
        return jsonify({'result': 'success', 'id': food.id})
    flash('Авторизуйтесь для совершения данного действия', category='alert alert-info')
    return jsonify({'result': 'error', 'login_page': url_for('auth.login')})

# Функция-представление удаления позиции/товара из избранного
@profile_bp.route('/favourites/delete', methods=['POST'])
@login_required
def delete_from_favourites():
    food_id = request.form.get('id')
    food = Food.query.get_or_404(food_id)

    # Если товара НЕТ в избранном и его пытаются удалить, то вернет JSON с ошибкой
    if food not in current_user.favs:
        return jsonify({'result': 'error', 'id': food.id})
        
    current_user.favs.remove(food)
    db.session.commit()
    return jsonify({'result': 'success', 'id': food.id})

# Функция-представление, возвращающая JSON с id товаров/позиций,
# которые есть в избранном у пользователя
@profile_bp.route('/favourites/api')
@login_required
def get_user_favourites():
    user_favourites = [food.id for food in current_user.favs]
    return jsonify(user_favourites)

# Функция-представление страницы профиля историей заказов
@profile_bp.route('/orders')
@login_required
def orders():
    orders = current_user.orders.all()
    return render_template('profile/orders.html', title='История заказов',
                            orders=orders, Food=Food, timezone=timezone, strftime=datetime.strftime)