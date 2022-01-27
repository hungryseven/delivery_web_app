from flask import jsonify, render_template, redirect, session, request, jsonify, url_for
from flask_login import current_user, login_required
from app.models import Food
from app.cart import bp as cart_bp
from app.cart.forms import OrderForm

# Функция-представление товаров в корзине
@cart_bp.route('/')
def cart():
    cart = session.get('cart', {})
    return render_template('cart/cart.html', title='Корзина', cart=cart, Food=Food)

@cart_bp.route('/order')
@login_required
def order():
    cart = session.get('cart', None)
    if cart is None:
        return redirect(url_for('cart.cart'))
    order_form = OrderForm()
    order_form.address.choices = [address for address in current_user.addresses]
    return render_template('cart/ordering.html', title='Оформление заказа', order_form=order_form)

# Функция-представление добавления товара/позиции в корзину.
# Если товара с таким id не существует, то выкинет 404 ошибку.
# Если товар УЖЕ в корзине и его пытаются добавить, то вернет JSON с ошибкой
@cart_bp.route('/add')
def add_to_cart():
    cart = session.setdefault('cart', {})
    food_id = request.args.get('id')
    food = Food.query.get_or_404(food_id)
    if str(food.id) in cart:
        return jsonify({'id': food.id, 'result': 'error'})
    cart[str(food.id)] = {}
    cart[str(food.id)]['quantity'] = 1
    cart[str(food.id)]['price'] = food.price
    session.modified = True
    return jsonify({'id': food.id, 'quantity': 1, 'price': food.price, 'result': 'success'})

# Функция-представление увеличения количества выбранного товара/позиции в корзине.
# Если товара с таким id не существует, то выкинет 404 ошибку.
# Если корзины в сессии не существует или товара с таким id нет в корзине,
# и происходит попытка увеличить его количество, то вернет JSON с ошибкой
@cart_bp.route('/increase')
def increase_quantity():
    cart = session.get('cart', None)
    food_id = request.args.get('id')
    food = Food.query.get_or_404(food_id)
    if cart is None or str(food.id) not in cart:
        return jsonify({'id': food.id, 'result': 'error'})
    cart[str(food.id)]['quantity'] += 1
    session.modified = True
    return jsonify({'id': food.id, 'quantity': cart[str(food.id)]['quantity'], 'price': food.price,'result': 'success'})

# Функция-представление уменьшения количества выбранного товара/позиции в корзине.
# Если товара с таким id не существует, то выкинет 404 ошибку.
# Если корзины в сессии не существует или товара с таким id нет в корзине,
# и происходит попытка уменьшить его количество, то вернет JSON с ошибкой.
# Если на момент уменьшения количества оно == 1, то удаляем id из сессии.
# Т.к. данного товара (ключа) нет в корзине (сессии), то в 'quantity' попадет 0 (блок try-except)
@cart_bp.route('/decrease')
def decrease_quantity():
    cart = session.get('cart', None)
    food_id = request.args.get('id')
    food = Food.query.get_or_404(food_id)
    if cart is None or str(food.id) not in cart:
        return jsonify({'id': food.id, 'result': 'error'})
    if cart[str(food.id)]['quantity'] == 1:
        cart.pop(str(food.id))
    elif cart[str(food.id)]['quantity'] > 1:
        cart[str(food.id)]['quantity'] -= 1
    try:
        quantity = cart[str(food.id)]['quantity']
    except KeyError:
        quantity = 0
    session.modified = True
    return jsonify({'id': food.id, 'quantity': quantity, 'price': food.price, 'result': 'success'})

# Функция-представление полного удаления товара/позиции из корзины.
# Если товара с таким id не существует, то выкинет 404 ошибку.
# Если корзины в сессии не существует или товара с таким id нет в корзине, то вернет JSON с ошибкой.
@cart_bp.route('/delete_item')
def delete_item():
    cart = session.get('cart', None)
    food_id = request.args.get('id')
    food = Food.query.get_or_404(food_id)
    if cart is None or str(food.id) not in cart:
        return jsonify({'id': food.id, 'result': 'error'})
    cart.pop(str(food.id))
    session.modified = True
    return jsonify({'id': food.id, 'result': 'success'})

# Функция-представление полной очистки корзины.
# Если корзины в сессии не существует или товара с таким id нет в корзине, то вернет JSON с ошибкой.
@cart_bp.route('/empty_the_cart')
def empty_the_cart():
    cart = session.get('cart', None)
    if cart is None:
        return jsonify({'result': 'error'})
    session.pop('cart')
    return jsonify({'result': 'success'})

# Функция-представление, возвращающая JSON с id товаров/позиций и их количеством,
# которые есть в корзине у пользователя.
# Если в сессии нет корзины, то вернет пустой словарь
@cart_bp.route('/api')
@login_required
def get_user_cart():
    cart = session.get('cart', {})
    return jsonify(cart)
