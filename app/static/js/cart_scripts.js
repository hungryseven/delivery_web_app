/* AJAX-запрос для добавления товара в корзину.
Скрывает кнопку "В корзину" и показывает кнопки
с возможностью уменьшения/увеличения количества товара
*/
$(function add_to_cart() {
    $('.cart-add').on('click', function() {
        var $this = $(this);
        var url_to_add = '/cart/add'
        var food_id = parseInt($this.attr('id').match(/\d+/));
        $.ajax({
            url: url_to_add,
            type: 'GET',
            dataType: 'json',
            data: {id: food_id},
            success: function(data) {
                $(`.cart-add#cart-add${food_id}`).addClass('visually-hidden');
                $(`.cart-plus-minus#cart-plus-minus${food_id}`).removeClass('visually-hidden');
                $(`.cart-quantity#cart-quantity${food_id}`).html(data['quantity']);
            },
            error: function() {
                console.log('Позиция уже в корзине');
            }
        });
    });
});

// AJAX-запрос для увеличения количества товара и изменения его суммарной цены
$(function increase_quantity() {
    $('.cart-increase').on('click', function() {
        var $this = $(this);
        total_price = parseInt($('.total-cart-price').text());
        var url_to_increase = '/cart/increase'
        var food_id = parseInt($this.attr('id').match(/\d+/));
        $.ajax({
            url: url_to_increase,
            type: 'GET',
            dataType: 'json',
            data: {id: food_id},
            success: function(data) {
                $(`.cart-quantity#cart-quantity${food_id}`).html(data['quantity']);
                $(`.food-price#food-price${food_id}`).html(data['quantity'] * data['price'] + '.00 р.');
                $('.total-cart-price').html(total_price + data['price'] + '.00 р.');
            }
        });
    });
});

/* AJAX-запрос для уменьшения количества товара и изменения его суммарной цены.
Если в данный момент количество товара == 1, и будет нажата кнопка уменьшения,
то на бэке товар удалится из сессии и data['quantity'] == 0.
В этом случае скрываются кнопки уменьшения/увеличения количества, и появится кнопка "В корзину".
Во всех остальных случаях меняется только количество
*/
$(function decrease_quantity() {
    $('.cart-decrease').on('click', function() {
        var $this = $(this);
        total_price = parseInt($('.total-cart-price').text());
        var url_to_decrease = '/cart/decrease'
        var food_id = parseInt($this.attr('id').match(/\d+/));
        $.ajax({
            url: url_to_decrease,
            type: 'GET',
            dataType: 'json',
            data: {id: food_id},
            success: function(data) {
                $(`.food-price#food-price${food_id}`).html(data['quantity'] * data['price'] + '.00 р.');
                $('.total-cart-price').html(total_price - data['price'] + '.00 р.');
                if (data['quantity'] == 0) {
                    $(`.cart-add#cart-add${food_id}`).removeClass('visually-hidden');
                    $(`.cart-plus-minus#cart-plus-minus${food_id}`).addClass('visually-hidden');
                    // Динамически удаляет карточку с товаром на странице корзины ('/cart')
                    $(`.cart-food#cart-food${food_id}`).remove();
                } else if (data['quantity'] >= 1) {
                    $(`.cart-quantity#cart-quantity${food_id}`).html(data['quantity']);
                };
            }
        });
    });
});

// AJAX-запрос для полного удаления определенного товара из корзины (с любым количеством)
$(function delete_item() {
    $('.cart-delete-item').on('click', function() {
        var $this = $(this);
        var url_to_delete = '/cart/delete_item'
        var food_id = parseInt($this.attr('id').match(/\d+/));
        $.ajax({
            url: url_to_delete,
            type: 'GET',
            dataType: 'json',
            data: {id: food_id},
            success: function(data) {
                $(`.cart-food#cart-food${food_id}`).remove();
            }
        });
    });
});

/* AJAX-запрос для полного удаления определенного товара из корзины (с любым количеством).
При удалении товаров скрывает блок с товарами и отображает блок с сообщением, что корзина пустая 
*/
$(function empty_the_cart() {
    $('.empty-the-cart').on('click', function() {
        var cards = $('.cart-food-cards')
        console.log(cards)
        var url_to_empty = '/cart/empty_the_cart'
        $.ajax({
            url: url_to_empty,
            type: 'GET',
            dataType: 'json',
            data: {},
            success: function() {
                $('.empty-cart').removeClass('visually-hidden');
                $('.non-empty-cart').addClass('visually-hidden');
            }
        });
    });
});

/* Функция получает JSON с id товаров и словарем с их количеством и ценой, которые находятся в корзине(сессии) пользователя.
При загрузке страницы скрывает кнопку "В корзину" и показывает кнопки с возможностью
уменьшения/увеличения количества товара.
Если корзина не пустая, то cкрывает блок, показывающий, что в корзине нет товаров и наоборот (переделать, выглядит стремновато)
*/
$(function get_user_cart() {
    var api_url = '/cart/api';
    var total_price = 0;
    $.getJSON(api_url, function(data) {
        if (JSON.stringify(data) !== '{}') {
            $('.empty-cart').addClass('visually-hidden');
            $('.non-empty-cart').removeClass('visually-hidden');
            for (let food_id in data) {
                total_price += data[food_id]['quantity'] * data[food_id]['price'];
                $(`.cart-add#cart-add${food_id}`).addClass('visually-hidden');
                $(`.cart-plus-minus#cart-plus-minus${food_id}`).removeClass('visually-hidden');
                $(`.cart-quantity#cart-quantity${food_id}`).html(data[food_id]['quantity']);
                $(`.food-price#food-price${food_id}`).html(data[food_id]['quantity'] * data[food_id]['price'] + '.00 р.')
            };
        } else {
            $('.empty-cart').removeClass('visually-hidden');
            $('.non-empty-cart').addClass('visually-hidden');
        };
        $('.total-cart-price').html(total_price + '.00 р.')
    });
});

