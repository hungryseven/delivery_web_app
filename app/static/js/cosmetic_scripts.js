/* Функция находит все ссылки навбаров на странице
и присваивает класс active тому, у которого совпадает ссылка
*/
$(function setNavActiveClass() {
    $('.nav-link').each(function() {
        if (this.href == location.href) {
            $(this).addClass('active');
        };
    });
});

// Аналогичная функция только для "хлебных крошек"
$(function setBreadActiveClass() {
    $('.breadcrumb-link').each(function() {
        if (this.href == location.href) {
            $(this).addClass('active');
        };
    });
});