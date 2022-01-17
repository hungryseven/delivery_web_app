from flask import render_template, url_for, redirect, flash, request, session
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from app import db
from app.models import User
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm, VerificationForm
from app.auth.phone_verification import request_verification_token, check_verification_token, parse_phone_number

# Функция-представление страницы логина и авторизации пользователя
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        phone_number = parse_phone_number(form.phone_number.data)[2:]
        user = User.query.filter_by(phone_number=phone_number).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный номер телефона или пароль')
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
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        phone_number = parse_phone_number(register_form.phone_number.data)
        request_verification_token(phone_number)
        session['first_name'] = register_form.first_name.data
        session['phone_number'] = phone_number
        session['password'] = register_form.password.data
        return redirect(url_for('auth.verify'))
    return render_template('auth/register.html', title='Регистрация', register_form=register_form)

@bp.route('/verify', methods=['GET', 'POST'])
def verify():
    verification_form = VerificationForm()
    if verification_form.validate_on_submit() and check_verification_token(session['phone_number'], verification_form.code.data):
        user = User(first_name=session['first_name'], phone_number=session['phone_number'][2:])
        user.set_password(session['password'])
        db.session.add(user)
        db.session.commit()
        session.pop('first_name')
        session.pop('phone_number')
        session.pop('password')
        flash('Вы успешно зарегистрировались!')
        return redirect(url_for('auth.login'))
    return render_template('auth/phone_verification.html', title='Подтверждение номера телефона', verification_form=verification_form)