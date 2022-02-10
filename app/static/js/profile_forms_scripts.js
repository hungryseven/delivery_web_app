/* Функция отображает ошибки полей при валидации.
Т.к. все формы создаются при помощи WTForms, а ошибки валидации
отображаются только при полной перезагрузке страницы, то не нашел
более адекватного способа, чем динамически создавать span'ы с ошибками при фейле валидации
*/
function showFieldsErrors(data, id='') {
    // Перед каждой новой валидацией удаляем ошибки предыдущей валидации
    $('.FieldError').remove();
    // Проходимся циклом в словаре по каждому полю, содержащему ошибку
    for (let field in data['errors']) {
        let field_errors = data['errors'][field];
        /* Проходимся циклом по списку ошибок каждого поля
        и добавляем ошибки после соответствующего инпута
        */
        for (let field_error of field_errors) {
            $(`input#${field}${id}`).after($('<span>', {
                class: 'FieldError',
                id: `error-${field}${id}`,
                style: 'color: red;',
                text: `${field_error}`
            }));
        };
    };
};

/* Функция отображает флеш-сообщение при успешном удалении адреса.
Причина рендеринга таким способом аналогична как и у функции выше
*/
function showFlashedMessage(text, category) {
    $('.flashed').remove();
    $('.profile-navbar').after($('<div>', {
        class: `container flashed ${category} text-center mb-5`,
        text: `${text}`
    }));
};

// AJAX-запрос для добавления адреса
$(function addAddress() {
    $('#AddAddressForm').on('submit', function(event) {
        var $this = $(this);
        var url_to_add = '/profile/address/add';
        $.ajax({
            url: url_to_add,
            type: 'POST',
            dataType: 'json',
            data: $this.serialize()
        })
        .done(function(data) {
            // Если результатом является ошибка валидации полей, то показываем эти ошибки
            if (data['result'] == 'error') {
                showFieldsErrors(data);
            // Иначе переходим на текущую страницу профиля с адресами
            } else {
                window.location = data['address_page'];
            };
        });
        event.preventDefault();
    });
});

// AJAX-запрос для редактирования адреса
$(function editAddress() {
    $('.EditAddressForm').on('submit', function(event) {
        var $this = $(this);
        var url_to_edit = '/profile/address/edit';
        var address_id = parseInt($this.attr('id').match(/\d+/));
        $.ajax({
            url: url_to_edit,
            type: 'POST',
            dataType: 'json',
            data: $this.serialize()
        })
        .done(function(data) {
            // Если результатом является ошибка валидации полей, то показываем эти ошибки
            if (data['result'] == 'error') {
                showFieldsErrors(data, id=address_id);
            // Иначе переходим на текущую страницу профиля с адресами
            } else {
                window.location = data['address_page'];
            };
        });
        event.preventDefault();
    });
});

// AJAX-запрос для удаления адреса
$(function deleteAddress() {
    $('.delete-address').on('click', function() {
        var $this = $(this);
        var url_to_delete = '/profile/address/delete';
        var address_id = parseInt($this.attr('id').match(/\d+/));
        $.ajax({
            url: url_to_delete,
            type: 'POST',
            dataType: 'json',
            data: {'id': address_id}
        })
        .done(function(data) {
            // Показываем флеш-сообщение об успешном удалении
            showFlashedMessage(data['flashed']['text'], data['flashed']['category']);
            // Удаляем карточку с адресом
            $(`#saved-address${address_id}`).remove();
        });
    });
});