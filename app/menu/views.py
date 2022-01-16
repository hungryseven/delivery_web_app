from turtle import title
from flask import render_template, redirect, url_for
from app.menu import bp
from app.main import bp as main_bp
from app.models import MenuCategory, Food

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
    category_name = MenuCategory.query.filter_by(slug=food_category).first()
    return render_template('menu/food_category.html', title=f'{category_name.name_category}', category=category_name)

# Функция-представление страниц каждой позиции/товара
@bp.route('/menu/<food_category>/<food>')
def food(food_category, food):
    food_name = Food.query.filter_by(slug=food).first()
    return render_template('menu/food.html', title=f'{food_name.name_food}', food=food_name)