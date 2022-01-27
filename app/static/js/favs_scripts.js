/* AJAX-запрос для добавления/удаления из избранного.
Если у кнопки есть класс "added", то удаляет его и товар из избранного,
если нет - добавляет.
*/
$(function favourites() {
    $('.favourites').on('click', function() {
        var $this = $(this);
        var food_id = parseInt($this.attr('id').match(/\d+/));
        var url_to_add = '/profile/favourites/add';
        var url_to_delete = '/profile/favourites/delete';
        if ($this.hasClass('added')) {
            $.ajax({
                url: url_to_delete,
                type: 'GET',
                dataType: 'json',
                data: {id: food_id},
                success: function() {
                    $this.removeClass('added');
                    $this.find('.bi-heart-fill').removeClass('bi-heart-fill').addClass('bi-heart');
                },
                error: function() {
                    console.log('Позиции нет в избранном');
                }
            });
        } else {
            $.ajax({
                url: url_to_add,
                type: 'GET',
                data: {id: food_id},
                success: function() {
                    $this.addClass('added');
                    $this.find('.bi-heart').removeClass('bi-heart').addClass('bi-heart-fill');
                },
                error: function() {
                    console.log('Позиция уже в избранном');
                }
            });
        };
    });
});

/* Функция получает JSON с id товаров, которые находятся в избранном у пользователя,
и при загрузке страницы меняет класс кнопки на "added"
*/
$(function get_user_favourites() {
    var api_url = '/profile/favourites/api';
    $.getJSON(api_url, function(data) {
        if (data.length != 0) {
            for (let food_id of data) {
                fav_btn = $(`.favourites#fav${food_id}`);
                fav_btn.addClass('added');
                fav_btn.find('.bi-heart').removeClass('bi-heart').addClass('bi-heart-fill');
            };
        };
    });
});

/* Функция удаляет карточку с товаром в профиле пользователя
при его удалении из избранного
*/
$(function delete_card() {
    var api_url = '/profile/favourites/api';
    $.getJSON(api_url, function(data) {
        if (data.length != 0) {
            for (let food_id of data) {
                $(`#fav${food_id}`).on('click', function() {
                    $(`.profile-favourites#food${food_id}`).remove();
                });
            };
        };
    });
});

