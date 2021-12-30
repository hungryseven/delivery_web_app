from flask import redirect, url_for, render_template
from flask_login import current_user
from app.profile import bp


@bp.route('/profile/info')
def info():
    return render_template('profile/info.html', title='Персональные данные')

@bp.route('/profile/address')
def address():
    return render_template('profile/address.html', title='Адрес доставки')

@bp.route('/profile/favourites')
def favourites():
    return render_template('profile/favourites.html', title='Избранное')

@bp.route('/profile/orders')
def orders():
    return render_template('profile/orders.html', title='История заказов')