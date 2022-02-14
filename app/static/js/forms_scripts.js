// Скрипты для форм на странице адресов в профиле ('profile/address')

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

// Скрипты для форм на странице персональной информации в профиле ('profile/info')

// AJAX-запрос для изменения пароля
$(function changePassword() {
    $('#ChangePasswordForm').on('submit', function(event) {
        var $this = $(this);
        var url_to_change = '/profile/info/change_password';
        $.ajax({
            url: url_to_change,
            type: 'POST',
            dataType: 'json',
            data: $this.serialize()
        })
        .done(function(data) {
            // Если результатом является ошибка ввода пароля, то показываем эту ошибку в флеш-сообщении
            if (data['result'] == 'password_error') {
                showFlashedMessage(data['flashed']['text'], data['flashed']['category']);
                // Очищаем поля формы
                $this[0].reset()
            // Если результатом является ошибка валидации полей, то показываем эти ошибки
            } else if (data['result'] == 'fields_error') {
                // Если до этого была ошибка ввода пароля, то удалим флеш для удобства восприятния инфы
                $('.flashed').remove();
                showFieldsErrors(data);
                $this[0].reset()
            // Иначе происходит смена пароля, показываем соответствующее флеш-сообщение
            } else {
                showFlashedMessage(data['flashed']['text'], data['flashed']['category']);
                // Сворачиваем коллапс при успешном изменении
                $('#PasswordFormCollapse').collapse('hide');
                $this[0].reset()
            };
        });
        event.preventDefault();
    });
});

// Скрипты для форм на странице персональной информации в профиле ('auth/login')

// AJAX-запрос для запроса телефона для восстановления пароля
$(function requestPhoneNumber() {
    $('#RequestForm').on('submit', function(event) {
        var $this = $(this);
        var url_to_request = '/auth/request_phone';
        $.ajax({
            url: url_to_request,
            type: 'POST',
            dataType: 'json',
            data: $this.serialize()
        })
        .done(function(data) {
            // Если результатом является ошибка валидации полей, то показываем эти ошибки
            if (data['result'] == 'error') {
                showFieldsErrors(data);
            // Иначе переходим на страницу ввода кода для подтверждения номера телефона
            } else {
                window.location = data['verify_page'];
            };
        });
        event.preventDefault();
    });
});