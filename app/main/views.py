from flask import render_template
from app.main import bp as main_bp
from flask_breadcrumbs import register_breadcrumb

@main_bp.route('/')
@register_breadcrumb(main_bp, '.', 'Главная')
def index():
    return render_template('main/main.html', title='Главная страница')