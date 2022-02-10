/* Функция отображает суммарное количество товаров в корзине на бадже,
если оно >= 1. Если оно == 0, то бадж скрывается
*/
function showTotalQuantity(selector, total_quantity) {
    if (total_quantity == 0) {
        selector.html('');
    } else if (total_quantity >= 1) {
        selector.html(total_quantity);
    };
};

// Функция блокирует кнопку "Оформить заказ", если суммарная цена меньше 1500
function disableGoToOrderingBtn(selector, total_price) {
    if (total_price < 1500) {
        selector.addClass('disabled');
    } else {
        selector.removeClass('disabled');
    };
};

/* AJAX-запрос для добавления товара в корзину.
Скрывает кнопку "В корзину" и показывает кнопки
с возможностью уменьшения/увеличения количества товара
*/
$(function addToCart() {
    $('.cart-add').on('click', function() {
        var $this = $(this);
        var url_to_add = '/cart/add'
        var food_id = parseInt($this.attr('id').match(/\d+/));
        $.ajax({
            url: url_to_add,
            type: 'POST',
            dataType: 'json',
            data: {'id': food_id}
        })
        .done(function(data) {
            // Меняем классы кнопок
            $(`.cart-add#cart-add${food_id}`).addClass('visually-hidden');
            $(`.cart-plus-minus#cart-plus-minus${food_id}`).removeClass('visually-hidden');
            // Ставим начальное количество товара == 1
            $(`.cart-quantity#cart-quantity${food_id}`).html(data['food_quantity']);
            // Обновляем бадж над корзиной с общим количеством товаров
            showTotalQuantity($('.cart-badge-quantity'), data['total_quantity']);
            // Блокируем кнопку, если сумма заказа < 1500
            disableGoToOrderingBtn($('.go-to-ordering-btn'), data['total_price']);
        });
    });
});

// AJAX-запрос для увеличения количества товара и изменения его суммарной цены
$(function increaseQuantity() {
    $('.cart-increase').on('click', function() {
        var $this = $(this);
        var total_price = parseInt($('.total-cart-price').text());
        var url_to_increase = '/cart/increase'
        var food_id = parseInt($this.attr('id').match(/\d+/));
        $.ajax({
            url: url_to_increase,
            type: 'POST',
            dataType: 'json',
            data: {'id': food_id}
        })
        .done(function(data) {
            // Меняем общее количество товара
            $(`.cart-quantity#cart-quantity${food_id}`).html(data['food_quantity']);
            // Меняем суммарную цену текущего товара товара и суммарную цену ВСЕГО заказа
            $(`.food-price#food-price${food_id}`).html(data['food_quantity'] * data['price'] + '.00 р.');
            $('.total-cart-price').html(total_price + data['price'] + '.00 р.');
            // Обновляем бадж над корзиной с общим количеством товаров
            showTotalQuantity($('.cart-badge-quantity'), data['total_quantity']);
            // Блокируем кнопку, если сумма заказа < 1500
            disableGoToOrderingBtn($('.go-to-ordering-btn'), data['total_price']);
        });
    });
});

/* AJAX-запрос для уменьшения количества товара и изменения его суммарной цены.
Если в данный момент количество товара == 1, и будет нажата кнопка уменьшения,
то на бэке товар удалится из сессии и data['quantity'] == 0.
В этом случае скрываются кнопки уменьшения/увеличения количества, и появится кнопка "В корзину".
Во всех остальных случаях меняется только количество
*/
$(function decreaseQuantity() {
    $('.cart-decrease').on('click', function() {
        var $this = $(this);
        var total_price = parseInt($('.total-cart-price').text());
        var url_to_decrease = '/cart/decrease'
        var food_id = parseInt($this.attr('id').match(/\d+/));
        $.ajax({
            url: url_to_decrease,
            type: 'POST',
            dataType: 'json',
            data: {'id': food_id}
        })
        .done(function(data) {
            // Меняем суммарную цену текущего товара товара и суммарную цену ВСЕГО заказа
            $(`.food-price#food-price${food_id}`).html(data['food_quantity'] * data['price'] + '.00 р.');
            $('.total-cart-price').html(total_price - data['price'] + '.00 р.');
            // Обновляем бадж над корзиной с общим количеством товаров
            showTotalQuantity($('.cart-badge-quantity'), data['total_quantity']);
            // Блокируем кнопку, если сумма заказа < 1500
            disableGoToOrderingBtn($('.go-to-ordering-btn'), data['total_price']);
            if (data['food_quantity'] == 0) {
                // Меняем классы кнопок
                $(`.cart-add#cart-add${food_id}`).removeClass('visually-hidden');
                $(`.cart-plus-minus#cart-plus-minus${food_id}`).addClass('visually-hidden');
                // Динамически удаляет карточку с товаром на странице корзины ('/cart')
                $(`.cart-food#cart-food${food_id}`).remove();
            } else if (data['food_quantity'] >= 1) {
                // Меняем общее количество товара
                $(`.cart-quantity#cart-quantity${food_id}`).html(data['food_quantity']);
            };
        });
    });
});

// AJAX-запрос для полного удаления определенного товара из корзины (с любым количеством)
$(function deleteItem() {
    $('.cart-delete-item').on('click', function() {
        var $this = $(this);
        var total_price = parseInt($('.total-cart-price').text());
        var url_to_delete = '/cart/delete_item';
        var food_id = parseInt($this.attr('id').match(/\d+/));
        $.ajax({
            url: url_to_delete,
            type: 'POST',
            dataType: 'json',
            data: {'id': food_id}
        })
        .done(function(data) {
            // Динамически удаляет карточку с товаром на странице корзины ('/cart')
            $(`.cart-food#cart-food${food_id}`).remove();
            // Меняем суммарную цену ВСЕГО заказа
            $('.total-cart-price').html(total_price - data['price'] * data['food_quantity'] + '.00 р.');
            // Обновляем бадж над корзиной с общим количеством товаров
            showTotalQuantity($('.cart-badge-quantity'), data['total_quantity']);
            // Блокируем кнопку, если сумма заказа < 1500
            disableGoToOrderingBtn($('.go-to-ordering-btn'), data['total_price']);
            // Если количество карточек с товарами на странице корзины ('/cart') == 0, то меняем классы блоков и отображаем пустую корзину
            if ($('.cart-food-cards').children().length == 0) {
                $('.empty-cart').removeClass('visually-hidden');
                $('.non-empty-cart').addClass('visually-hidden');
            };
        });
    });
});

/* AJAX-запрос для полного удаления определенного товара из корзины (с любым количеством).
При удалении товаров скрывает блок с товарами и отображает блок с сообщением, что корзина пустая 
*/
$(function emptyTheCart() {
    $('.empty-the-cart').on('click', function() {
        var url_to_empty = '/cart/empty_the_cart';
        $.ajax({
            url: url_to_empty,
            type: 'POST',
            dataType: 'json',
            data: {}
        })
        .done(function() {
            // Удаляем бадж с общим
            showTotalQuantity($('.cart-badge-quantity'), 0);
            // Меняем классы блоков с информацией о пустой/полной корзине
            $('.empty-cart').removeClass('visually-hidden');
            $('.non-empty-cart').addClass('visually-hidden');
        });
    });
});

/* Функция получает JSON с id товаров и словарем с их количеством и ценой, которые находятся в корзине(сессии) пользователя.
При загрузке страницы скрывает кнопку "В корзину" и показывает кнопки с возможностью
уменьшения/увеличения количества товара. Показывает бадж над корзиной с текущим количеством товаров.
Если корзина не пустая, то cкрывает блок, показывающий, что в корзине нет товаров и наоборот (переделать, выглядит стремновато)
*/
$(function getUserCart() {
    var api_url = '/cart/cart_api';
    var total_price = 0;
    var total_quantity = 0;
    $.getJSON(api_url, function(data) {
        if (JSON.stringify(data) !== '{}') {
            // Меняем классы блоков, отображая список товаров в корзине (JSON не пустой)
            $('.empty-cart').addClass('visually-hidden');
            $('.non-empty-cart').removeClass('visually-hidden');
            for (let food_id in data) {
                total_price += data[food_id]['quantity'] * data[food_id]['price'];
                total_quantity += data[food_id]['quantity'];
                // Меняем классы кнопок, количество товара и суммарную цену для тех товаров, которые находятся в корзине
                $(`.cart-add#cart-add${food_id}`).addClass('visually-hidden');
                $(`.cart-plus-minus#cart-plus-minus${food_id}`).removeClass('visually-hidden');
                $(`.cart-quantity#cart-quantity${food_id}`).html(data[food_id]['quantity']);
                $(`.food-price#food-price${food_id}`).html(data[food_id]['quantity'] * data[food_id]['price'] + '.00 р.')
            };
        } else {
            // Меняем классы блоков, отображая, что корзина пустая (JSON пустой)
            $('.empty-cart').removeClass('visually-hidden');
            $('.non-empty-cart').addClass('visually-hidden');
        };
        $('.total-cart-price').html(total_price + '.00 р.')
        // Показываем бадж над корзиной с общим количеством товаров, если их >= 1
        showTotalQuantity($('.cart-badge-quantity'), total_quantity);
        // Блокируем кнопку, если сумма заказа < 1500
        disableGoToOrderingBtn($('.go-to-ordering-btn'), total_price);
    });
});

/* AJAX-запрос для вставки данных сохраненных адресов пользователя
при выборе соответсвующего option в select
*/
$(function insertAddress() {
    $('#addresses').on('change', function() {
        var selectedOption = $(this).find('option:selected');
        var address_id = selectedOption.val();
        var url_to_insert = '/cart/order/insert_address';
        $.ajax({
            url: url_to_insert,
            type: 'POST',
            dataType: 'json',
            data: {'id': address_id}
        })
        .done(function(data) {
            $('#street').val(data['street']);
            $('#house').val(data['house']);
            $('#building').val(data['building']);
            $('#entrance').val(data['entrance']);
            $('#floor').val(data['floor']);
            $('#apartment').val(data['apartment']);
            $('#additional_info').val(data['additional_info']);
        });
    });
});

/* AJAX-запрос меняет варианты выбора времени доставки
при выборе соответствующего option в select с датами
*/
$(function setTimeChoices() {
    $('#date').on('change', function() {
        var selectedOption = $(this).find('option:selected');
        var timeSelect = $('#time');
        var date = selectedOption.val();
        var url_to_set = '/cart/order/set_time_choices';
        $.ajax({
            url: url_to_set,
            type: 'POST',
            dataType: 'json',
            data: {
                'date': date
            }
        })
        .done(function(data) {
            // Удаляем всех потомков перед изменением
            timeSelect.empty();
            for (let elem of data) {
                timeSelect.append($('<option>', {
                    value: elem['value'],
                    text: elem['text']
                }));
            };
        });
    }).change();
});