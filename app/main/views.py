from flask import render_template
from sqlalchemy import func, desc
from app import db
from app.main import bp as main_bp
from app.models import OrderFood, Food, MenuCategory
from flask_breadcrumbs import register_breadcrumb

def find_popular_foods(categories):
    '''
    Функция возвращает 4 самых популярных позиции из меню для каждой переданной категории
    (т.е. те позиции, которые заказывали чаще всего по количеству)

        Параметры:
                    categories (list): Список категорий (экземпляров класса MenuCategory)

        Вовзвращаемое значение:

                    popular_food (dict): Словарь вида {Наименование_категории: [food_id1,..., food_id4],...}
                                            с 4 самыми популярными позициями дл каждой переданной категории
    '''
    popular_foods = {}
    for category in categories:

        # Аналог запроса
        # SELECT food.id, SUM(order_food.food_quantity) AS quantity
        # FROM food
        # LEFT JOIN order_food
        #     ON food.id = order_food.food_id
        # LEFT JOIN menu_category
        #     ON food.category_id = menu_category.id
        # WHERE menu_category.name_category = category.name_category
        # GROUP BY(food.id)
        # ORDER BY(quantity) DESC
        # LIMIT 4
        category_popular_foods = db.session.query(Food.id, func.sum(OrderFood.food_quantity).label('quantity')). \
            outerjoin(OrderFood, Food.id==OrderFood.food_id). \
            outerjoin(MenuCategory, MenuCategory.id==Food.category_id). \
            filter_by(name_category=category.name_category). \
            group_by(Food.id). \
            order_by((desc('quantity')).nullslast()). \
            limit(4).all()
        
        # Достаем из каждого кортежа id позиции/товара
        category_popular_foods = [food[0] for food in category_popular_foods]

        popular_foods[category.name_category] = category_popular_foods
    return popular_foods

        
# Функция-представление для главной страницы
@register_breadcrumb(main_bp, '.', 'Главная')
@main_bp.route('/')
def index():

    # Запрос, который вернет 5 категорий по их приоритету в порядке возрастания
    categories = db.session.query(MenuCategory).order_by(MenuCategory.order).limit(5).all()
    
    popular_foods = find_popular_foods(categories)
    return render_template('main/main.html', title='Главная страница', popular_foods=popular_foods, Food=Food, MenuCategory=MenuCategory)

# Функция-представление для информации о доставке
@main_bp.route('/delivery')
def delivery():
    return render_template('main/delivery.html', title='Доставка')

# Функция-представление для информации клиентам
@main_bp.route('/clients')
def clients():
    return render_template('main/clients.html', title='Клиентам')

# Функция-представление для новостей
@main_bp.route('/news')
def news():
    return render_template('main/news.html', title='Новости')