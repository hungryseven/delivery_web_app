from flask import render_template, redirect, url_for
from app.menu import bp
from app.models import MenuCategory

@bp.route('/menu')
def menu():
    categories = MenuCategory.query.all()
    categories = sorted(categories, key=lambda x: x.order)
    return render_template('menu/menu.html', title='Меню', categories=categories)