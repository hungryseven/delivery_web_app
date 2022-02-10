// Функция устанавливает CSRFToken в заголовок запроса перед отправкой AJAX-запроса
$(function setCSRFToken() {
    var csrf_token = $('meta[name="csrf-token"]').attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            };
        }
    });
});