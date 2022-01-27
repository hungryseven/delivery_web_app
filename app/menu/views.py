from flask import render_template, request, url_for
from app.main import bp as main_bp
from app.menu import bp as menu_bp
from app.models import MenuCategory, Food
from flask_breadcrumbs import default_breadcrumb_root, register_breadcrumb, current_breadcrumbs, current_path

default_breadcrumb_root(main_bp, '.')

# Функция-представление страницы главного меню по категориям
@menu_bp.route('/')
@register_breadcrumb(menu_bp, '.', 'Меню')
def menu():
    categories = MenuCategory.query.all()
    # Сортировка по приоритету (order) для желаемого отображения на странице
    categories = sorted(categories, key=lambda x: x.order)
    return render_template('menu/menu.html', title='Меню', categories=categories)

# Функция для определения текущей категории,
# которая будет отображаться в "хлебных крошках"
def view_food_category_dlc(*args, **kwargs):
    category_slug = request.view_args['food_category']
    category = MenuCategory.query.filter_by(slug=category_slug).first()
    return [{'text': category.name_category, 'url': url_for('menu.food_category', food_category=category.slug)}]

# Функция-представление страниц еды/товаров каждой категории
@menu_bp.route('/<food_category>')
@register_breadcrumb(menu_bp, '.food_category', '', dynamic_list_constructor=view_food_category_dlc)
def food_category(food_category):
    category = MenuCategory.query.filter_by(slug=food_category).first()
    return render_template('menu/food_category.html', title=f'{category.name_category}', category=category)

# Функция для определения текущей позиции еды/товара,
# которая будет отображаться в "хлебных крошках"
def view_food_dlc(*args, **kwargs):
    food_slug = request.view_args['food']
    food = Food.query.filter_by(slug=food_slug).first()
    category = food.category
    return [{'text': food.name_food, 'url': url_for('menu.food', food_category=category.slug, food=food.slug)}]

# Функция-представление страниц каждой позиции/товара
@menu_bp.route('/<food_category>/<food>')
@register_breadcrumb(menu_bp, '.food_category.food', '', dynamic_list_constructor=view_food_dlc)
def food(food_category, food):
    food = Food.query.filter_by(slug=food).first()
    return render_template('menu/food.html', title=f'{food.name_food}', food=food)