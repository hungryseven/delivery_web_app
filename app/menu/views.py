from flask import render_template, redirect, url_for
from app.menu import bp
from app.models import MenuCategory

# Функция-представление страницы главного меню по категориям
@bp.route('/menu')
def menu():
    categories = MenuCategory.query.all()
    # Сортировка по приоритету (order) для желаемого отображения на странице
    categories = sorted(categories, key=lambda x: x.order)
    return render_template('menu/menu.html', title='Меню', categories=categories)

# Функция-представление страниц еды/товаров каждой категории
@bp.route('/menu/<food_category>')
def food_category(food_category):
    category = MenuCategory.query.filter_by(slug=food_category).first()
    return render_template('menu/food_category.html', title=f'{category.name_category}', category=category)