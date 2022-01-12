from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from app import db
from app.models import User
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm

# Функция-представление страницы логина и авторизации пользователя
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный email или пароль')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # Парсим URL на наличие 'next' аргумента строки запроса,
        # чтобы пользователь после авторизации вернулся к желаемой
        # странице, если она защищена от анонимного просмотра.
        # Если у URL нет 'next' аргумента или аргумент 'next'
        # включает в себя полный URL с именем домена, то происходит
        # редирект на главную страницу
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Авторизация', form=form)

# Функция-представление выхода из профиля
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# Функция-представление страницы регистрации пользователя
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()  
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Регистрация', form=form)
