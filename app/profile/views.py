from flask import redirect, url_for, render_template, flash
from flask_login import current_user, login_required
from app import db
from app.models import User
from app.profile import bp
from app.profile.forms import InfoForm, PasswordForm


@bp.route('/profile/info', methods=['GET', 'POST'])
@login_required
def info():
    info_form = InfoForm()
    password_form = PasswordForm()
    if info_form.submit_info.data and info_form.validate():
        current_user.sex = info_form.sex.data
        current_user.first_name = info_form.first_name.data
        current_user.phone_number = info_form.phone_number.data
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

@bp.route('/profile/address', methods=['GET', 'POST'])
@login_required
def address():
    return render_template('profile/address.html', title='Адрес доставки')

@bp.route('/profile/favourites')
@login_required
def favourites():
    return render_template('profile/favourites.html', title='Избранное')

@bp.route('/profile/orders')
@login_required
def orders():
    return render_template('profile/orders.html', title='История заказов')