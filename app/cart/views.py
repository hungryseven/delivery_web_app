from cProfile import label
from cgitb import text
from flask import jsonify, render_template, redirect, session, request, jsonify, url_for, flash, abort
from flask_login import current_user, login_required
from app import db, csrf
from app.models import Food, Address, Order, OrderFood
from app.cart import bp as cart_bp
from app.cart.forms import OrderForm
from app.auth.phone_verification import parse_phone_number
from datetime import date, datetime, timedelta, timezone
import math

def calculate_total_quantity(cart):
    '''
    Функция возвращает суммарное количество товаров в корзине

        Параметры:
                    cart (dict): словарь в сессии типа { food_id: {'price': value, 'quantity': value} }
        
        Возвращаемое значение:
                    total_quantity (int): суммарное количество товаров в корзине
    '''
    total_quantity = sum([cart[food_id]['quantity'] for food_id in cart])
    return total_quantity

def calculate_total_price(cart):
    '''
    Функция возвращает суммарную цену всего заказа

        Параметры:
                    cart (dict): словарь в сессии типа { food_id: {'price': value, 'quantity': value} }
        
        Возвращаемое значение:
                    total_price (int): суммарная цена всего заказа
    '''
    total_price = sum([cart[food_id]['quantity'] * cart[food_id]['price'] for food_id in cart])
    return total_price

def set_date_choices(field, number_of_choices):
    '''
    Функция добавляет в список 'field.choices' SelectField'a варианты дат 
    от текущего дня до дня, определенного параметром 'number_of_choices'

        Параметры:
                    field (class 'wtforms.fields.choices.SelectField'): SelectField поле формы
                    number_of_choices (int): количество вариантов дат (тегов option в теге select)
        
        Возвращаемое значение:
                    None
    '''
    current_date = date.today()
    for i in range(number_of_choices):
        appending_date = current_date + timedelta(days=i)

        # Если добавляемая дата == текущей, то в текст тега записываем "Сегодня"
        if appending_date == current_date:
            field.choices.append((appending_date, 'Сегодня'))

        # Если добавляемая дата == текущая + 1 день, то в текст тега записываем "Завтра"
        elif appending_date == current_date + timedelta(days=1):
            field.choices.append((appending_date, 'Завтра'))

        else:
            field.choices.append((appending_date, appending_date.strftime('%d.%m')))

def ceil_dt_to_quarter(dt):
    '''
    Функция округляет переданный экземпляр класса datetime.datetime до ближайшей четверти часа

        Параметры:
                    dt (class 'datetime.datetime'): экземпляр класса datetime.datetime
        
        Возвращаемое значение:
                    Объект (class 'datetime.datetime'): время, округленное до ближайшей четверти часа
    '''
    seconds = dt.minute * 60 + dt.second + dt.microsecond * 10 ** (-6)

    # Определяем в какой четверти часа находится время и находим необходимую разницу, которую нужно прибавить
    delta = math.ceil(seconds / 900) * 900 - seconds
    return dt + timedelta(seconds=delta)

def create_time_choices(selected_date, opening_time=datetime(2022, 1, 1, 9, 15), closing_time=datetime(2022, 1, 1, 23),
                        first_delivery=datetime(2022, 1, 1, 10, 45), delivery_time=timedelta(hours=1, minutes=30),
                        time_step=timedelta(minutes=15), endday_time=datetime(2022, 1, 1, 23, 59, 59)):
    '''
    Функция возвращает список из кортежей вида ('value': datetime.datetime inst, 'text': text) достопного
    времени для доставки в зависимости от выбранного дня. Во всех экземплярах класса datetime.datetime
    стоит фиктивная дата для возможности сложения с timedelta. В аттрибут тега option попадает UTC время,
    которое записывается в БД, в innerHTML тега option попадает локальное время.

        Параметры:
                    selected_date (str): выбранная дата в формате 'year-day-month'
                    opening_time (class 'datetime.datetime'): время начала работы
                    closing_time (class 'datetime.datetime'): время окончания работы работы
                    first_delivery (class 'datetime.datetime'): время первой возможной доставки за день
                    delivery_time (class 'datetime.timedelta'): время доставки заказа
                    time_step (class 'datetime.timedelta'): шаг времени для выбора времени доставки (11:00, 11:15 и т.д.)
                    endday_time (class 'datetime.datetime'): время окончания дня
        
        Возвращаемое значение:
                    time_choices (list): список кортежей со значениями (value - аттрибут тега option)
                                            и текстом (text - innerHTML тега option)
    '''
    # Конвертируем дату из строки в класс datetime.date
    selected_date = selected_date.split('-')
    selected_date = map(int, selected_date)
    selected_date = date(*selected_date)

    current_date = date.today()
    time_choices = []
    if selected_date == current_date:
        current_time = datetime.now()

        # Если текущее время находится в промежутке между открытием и закрытием 9:15 - 23:00 (далее указавается локальное время)
        if opening_time.time() <= current_time.time() < closing_time.time():

            # Если текущее время находится в промежутке между 21:30 - 23:00,
            # то для выбора будет доступно только значение "Ближайшее".
            # Следующему времени приваивается пустая строка
            if (closing_time - delivery_time).time() <= current_time.time() < closing_time.time():
                time_choices.append(
                    {'value': str(closing_time.astimezone(timezone.utc).time()), 'text': 'Ближайшее'}
                )
                time_choice = ''
            
            # Иначе (время в промежутке 9:15 - 21:30) ближайшее время = текущее + время доставки.
            # Значению следующего времени присваивается время, округленное до ближайшей четверти часа вперед
            else:
                first_time_choice = current_time + delivery_time
                time_choices.append(
                    {'value': str(first_time_choice.astimezone(timezone.utc).time()), 'text': 'Ближайшее'}
                )
                time_choice = ceil_dt_to_quarter(first_time_choice)
        
        # Если текущее время в промежутке 23:00 - 23:59:59, то вариантов для выбора нет
        elif closing_time.time() <= current_time.time() <= endday_time.time():
            time_choice = ''
        
        # Если текущее время в промежутке 00:00 - 9:15, то доступно любое время в промежутке 10:45 - 23:00
        else:
            time_choice = first_delivery

    #Если выбран другой любой день, кроме текущего, то доступно любое время в промежутке 10:45 - 23:00
    else:
        time_choice = first_delivery

    # Если существует следующее значение времени доставки (не пустая строка), то добавляем его, и, далее,
    # добавляем время с интервалом time_step пока оно не станет больше 23:00
    if time_choice:
        time_choices.append(
            {'value': str(time_choice.astimezone(timezone.utc).time()), 'text': time_choice.strftime('%H:%M')}
        )
        while time_choice.time() < closing_time.time():
            time_choice += time_step
            time_choices.append(
                {'value': str(time_choice.astimezone(timezone.utc).time()), 'text': time_choice.strftime('%H:%M')}
            )

    return time_choices

# Функция принимает дату и время из двух разных полей формы (тип str) и возвращает экземпляр класса datetime
def create_datetime_inst(date, time):
    '''
    Функция возвращает экземпляр класса datetime. Реализована, потому что дата и время берутся из разных полей,
    чтобы занести в БД полное значение
        Параметры:
                    date (str): дата в формате 'year-day-month'
                    time (str): время в формате 'hour:minute:second:microsecond'
        
        Возвращаемое значение:
                    Объект (class 'datetime.datetime'): объединенное значение даты и времени
    '''
    date_list = date.split('-')
    time_list = time.replace('.', ':').split(':')
    datetime_list = date_list + time_list
    datetime_list = map(int, datetime_list)
    return datetime(*datetime_list)

# Функция принимает data из полей формы с адресом и возвращает полный адрес в более читаемом виде
def format_address(street, house, building, *fields):
    '''
    Функция возвращает полный адрес, указанный в форме доставки. Если значение поля пустое - элемент адреса игнорируется.
        Параметры:
                    street (str): Название улицы
                    house (str): Номер дома
                    building (str): Строение
                    *fields (list): Остальные элементы адреса
        
        Возвращаемое значение:
                    address (str): Полный адрес доставки
    '''
    address = f'Улица {street} {house}{building}. '
    for field in fields:
        if field.data:
            address += f'{field.label.text} - {field.data}. '
    return address

# Функция-представление товаров в корзине
@cart_bp.route('/')
def cart():
    cart = session.get('cart', {})
    return render_template('cart/cart.html', title='Корзина', cart=cart, Food=Food)

# Функция-представление для оформления заказа
@cart_bp.route('/order', methods=['GET', 'POST'])
def order():
    cart = session.get('cart', None)

    # Если суммарная стоимость коризны < 1500 или корзины не существует, то произойдет редирект на страницу корзины
    if calculate_total_price(cart) < 1500 or cart is None:
        return redirect(url_for('cart.cart'))

    order_form = OrderForm()
    set_date_choices(order_form.date, 8)

    # Если юзер авторизован, то ищем все его сохраненные адреса и добавляем в SelectField в качестве выбора
    if current_user.is_authenticated:
        user_addresses = current_user.addresses.all()
        for address in user_addresses:
            order_form.addresses.choices.append((address.id, address))

    if order_form.validate_on_submit():
        order = Order(
            first_name=order_form.first_name.data,
            phone_number=parse_phone_number(order_form.phone_number.data)[2:],
            address=format_address(order_form.street.data, order_form.house.data, order_form.building.data,
                                    order_form.entrance, order_form.floor, order_form.apartment, order_form.additional_info),
            delivery_datetime=create_datetime_inst(order_form.date.data, order_form.time.data),
            payment_method=order_form.payment_method.data,
            total_price=calculate_total_price(cart),
            persons=order_form.number_of_persons.data[0],
            order_notes=order_form.order_notes.data,

            # Если заказ был оформлен анонимным пользователем, то его его id в БД == 0
            user_id=current_user.id if current_user.is_authenticated else 0
        )

        db.session.add(order)

        # Добавляем в БД позиции товара и их количество в текущем заказе
        for food_id in cart:
            food = Food.query.get(food_id)
            order_food = OrderFood(food_quantity=cart[food_id]['quantity'], food=food, order=order)
            db.session.add(order_food)

        db.session.commit()
        session.pop('cart')
        flash('Заказ успешно оформлен. Ожидайте звонка оператора для подтверждения заказа', category='alert alert-success')
        return redirect(url_for('cart.cart'))     
    return render_template('cart/ordering.html', title='Оформление заказа', order_form=order_form)

# Функция-представление для повторения заказов, которые уже были оформлены пользователем
@cart_bp.route('/repeat_order/<order_id>')
@login_required
def repeat_order(order_id):
    order = Order.query.get_or_404(order_id)

    # Если у текущего юзера не было заказа с таким id, то выкинет 404 ошибку
    if order not in current_user.orders:
        abort(404)
    
    # Если корзина есть в сессии, то очищаем ее, если нет - создаем
    cart = session.setdefault('cart', {})
    cart.clear()

    # Добавляем в сессию все товары и их количество из выбранного заказа
    for food in order.foods:
        food_inst = Food.query.get(food.food_id)
        cart[food.food_id] = {}
        cart[food.food_id]['price'] = food_inst.price
        cart[food.food_id]['quantity'] = food.food_quantity
    session.modified = True
    return redirect(url_for('cart.cart'))

# Функция-представление добавления товара/позиции в корзину
@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    cart = session.setdefault('cart', {})
    food_id = request.form.get('id')
    food = Food.query.get_or_404(food_id)

    # Если товар УЖЕ в корзине и его пытаются добавить, то вернет JSON с ошибкой
    if str(food.id) in cart:
        return jsonify({'result': 'error', 'id': food.id})

    cart[str(food.id)] = {}
    cart[str(food.id)]['quantity'] = 1
    cart[str(food.id)]['price'] = food.price
    session.modified = True
    total_quantity = calculate_total_quantity(cart)
    total_price = calculate_total_price(cart)
    return jsonify(
        {
            'result': 'success',
            'id': food.id,
            'food_quantity': 1,
            'total_quantity': total_quantity,
            'total_price': total_price,
            'price': food.price
        }
    )

# Функция-представление увеличения количества выбранного товара/позиции в корзине
@cart_bp.route('/increase', methods=['POST'])
def increase_quantity():
    cart = session.get('cart', None)
    food_id = request.form.get('id')
    food = Food.query.get_or_404(food_id)

    # Если корзины в сессии не существует или товара с таким id нет в корзине,
    # и происходит попытка увеличить его количество, то вернет JSON с ошибкой
    if cart is None or str(food.id) not in cart:
        return jsonify({'result': 'error', 'id': food.id})

    cart[str(food.id)]['quantity'] += 1
    session.modified = True
    quantity = cart[str(food.id)]['quantity']
    total_quantity = calculate_total_quantity(cart)
    total_price = calculate_total_price(cart)
    return jsonify(
        {
            'result': 'success',
            'id': food.id,
            'food_quantity': quantity,
            'total_quantity': total_quantity,
            'total_price': total_price,
            'price': food.price
        }
    )

# Функция-представление уменьшения количества выбранного товара/позиции в корзине
@cart_bp.route('/decrease', methods=['POST'])
def decrease_quantity():
    cart = session.get('cart', None)
    food_id = request.form.get('id')
    food = Food.query.get_or_404(food_id)

    # Если корзины в сессии не существует или товара с таким id нет в корзине,
    # и происходит попытка уменьшить его количество, то вернет JSON с ошибкой
    if cart is None or str(food.id) not in cart:
        return jsonify({'result': 'error', 'id': food.id})
    
    # Если на момент уменьшения количества оно == 1, то удаляем id из сессии
    if cart[str(food.id)]['quantity'] == 1:
        cart.pop(str(food.id))

    elif cart[str(food.id)]['quantity'] > 1:
        cart[str(food.id)]['quantity'] -= 1

    # Получаем значение количества товара после его уменьшения.
    # Т.к. данного товара (ключа) нет в корзине (сессии), то в 'quantity' попадет 0
    try:
        quantity = cart[str(food.id)]['quantity']
    except KeyError:
        quantity = 0

    session.modified = True
    total_quantity = calculate_total_quantity(cart)
    total_price = calculate_total_price(cart)
    return jsonify(
        {
            'result': 'success',
            'id': food.id,
            'food_quantity': quantity,
            'total_quantity': total_quantity,
            'total_price': total_price,
            'price': food.price
        }
    )

# Функция-представление полного удаления товара/позиции из корзины
@cart_bp.route('/delete_item', methods=['POST'])
def delete_item():
    cart = session.get('cart', None)
    food_id = request.form.get('id')
    food = Food.query.get_or_404(food_id)
    quantity = cart[str(food.id)]['quantity']

    # Если корзины в сессии не существует или товара с таким id нет в корзине, то вернет JSON с ошибкой
    if cart is None or str(food.id) not in cart:
        return jsonify({'result': 'error', 'id': food.id})

    cart.pop(str(food.id))
    session.modified = True
    total_quantity = calculate_total_quantity(cart)
    total_price = calculate_total_price(cart)
    return jsonify(
        {
            'result': 'success',
            'id': food.id,
            'food_quantity': quantity,
            'total_quantity': total_quantity,
            'total_price': total_price,
            'price': food.price,
        }
    )

# Функция-представление полной очистки корзины.
@cart_bp.route('/empty_the_cart', methods=['POST'])
def empty_the_cart():
    cart = session.get('cart', None)

    # Если корзины в сессии не существует, то вернет JSON с ошибкой
    if cart is None:
        return jsonify({'result': 'error'})

    session.pop('cart')
    return jsonify({'result': 'success'})

# Функция-представление, возвращающая JSON с id товаров/позиций и их количеством,
# которые есть в корзине у пользователя.
# Если в сессии нет корзины, то вернет пустой словарь
@cart_bp.route('/cart_api')
def get_user_cart():
    cart = session.get('cart', {})
    return jsonify(cart)

# Функция-представление добавления в поля формы данных сохраненных адресов пользователей.
# Вставляет все сохраненные ранее значения. Если выбран пункт "Указать новый адрес", то очищает поля формы
@cart_bp.route('/order/insert_address', methods=['POST'])
def insert_address():
    address_id = request.form.get('id')
    if address_id == '0':
        return jsonify(
            {
                'street': '',
                'house': '',
                'building': '',
                'entrance': '',
                'floor': '',
                'apartment': '',
                'additional_info': ''
            }
        )
    address = Address.query.get_or_404(address_id)

    # Если у текущего юзера нет сохранненого адреса с таким id, то вернет JSON с ошибкой
    if address not in current_user.addresses.all():
        return jsonify({'result': 'error', 'id': address.id})

    return jsonify(
        {
            'street': address.street,
            'house': address.house,
            'building': address.building,
            'entrance': address.entrance,
            'floor': address.floor,
            'apartment': address.apartment,
            'additional_info': address.additional_info
        }
    )

# Функция-представление устанавливает варианты вабора времени доставки заказа
# в зависимости от выбранной даты
@cart_bp.route('/order/set_time_choices', methods=['POST'])

# Выключил CSRF защиту на эту фукнцию, т.к. перестал работать скрипт при загрузке страницы.
# Пока не знаю, как пофиксить
@csrf.exempt
def set_time_choices(): 
    date = request.form.get('date')
    time_choices = create_time_choices(date)
    return jsonify(time_choices)