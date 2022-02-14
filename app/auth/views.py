from flask import render_template, url_for, redirect, flash, request, session, jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from app import db
from app.models import User
from app.auth import bp as auth_bp
from app.auth.forms import LoginForm, RegisterForm, VerificationForm, PhoneRequestForm, ResetPasswordForm
from app.auth.phone_verification import request_verification_token, check_verification_token, parse_phone_number

# Функция-представление страницы логина и авторизации пользователя
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    login_form = LoginForm()
    request_form = PhoneRequestForm()
    if login_form.validate_on_submit():
        phone_number = parse_phone_number(login_form.phone_number.data)[2:]
        user = User.query.filter_by(phone_number=phone_number).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Неверный номер телефона или пароль', category='alert alert-danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=login_form.remember_me.data)

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

    return render_template('auth/login.html', title='Авторизация', login_form=login_form, request_form=request_form)

# Функция-представление запроса номера телефона для восстановления пароля
@auth_bp.route('/request_phone', methods=['POST'])
def request_phone():
    request_form = PhoneRequestForm()
    if request_form.validate_on_submit():
        phone_number = parse_phone_number(request.form.get('requested_phone'))
        request_verification_token(phone_number)
        session['phone_number'] = phone_number
        return jsonify(
            {
                'result': 'success',
                'verify_page': url_for('auth.verify', action='reset_password_verify')
            }
        )

    # Возвращаем ошибки валидации полей формы
    return jsonify({'result': 'error', 'errors': request_form.errors})

# Функция-представление выхода из профиля
@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# Функция-представление страницы регистрации пользователя
@auth_bp.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('auth.verify', action='register_verify'))
    return render_template('auth/register.html', title='Регистрация', register_form=register_form)

# Функция-представление страницы подтверждения номера телефона
# при регистрации/восстановлении пароля
@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    verification_form = VerificationForm()
    action = request.args.get('action', '')

    # Если на страницу подтверждения номера телефона пытаются зайти не через регистрацию/восстановление пароля,
    # то редиректим на главную страницу
    if not action:
        return redirect(url_for('main.index'))

    # Условие выполнится, если код подтверждения будет запрашиваться
    # при регистрации
    elif action == 'register_verify':
        if verification_form.validate_on_submit() and check_verification_token(session['phone_number'], verification_form.code.data):
            user = User(first_name=session['first_name'], phone_number=session['phone_number'][2:])
            user.set_password(session['password'])
            db.session.add(user)
            db.session.commit()
            session.pop('first_name')
            session.pop('phone_number')
            session.pop('password')
            flash('Вы успешно зарегистрировались!', category='alert alert-success')
            return redirect(url_for('auth.login'))
        elif verification_form.validate_on_submit() and not check_verification_token(session['phone_number'], verification_form.code.data):
            flash('Неверный код подтверждения', category='alert alert-danger')
            return redirect(url_for('auth.verify', action=action))
            
    # Условие выполнится, если код подтверждения будет запрашиваться
    # при восстановлении пароля 
    elif action == 'reset_password_verify':
        if verification_form.validate_on_submit() and check_verification_token(session['phone_number'], verification_form.code.data):
            return redirect(url_for('auth.reset_password', prev='true'))
        elif verification_form.validate_on_submit() and not check_verification_token(session['phone_number'], verification_form.code.data):
            flash('Неверный код подтверждения', category='alert alert-danger')
            return redirect(url_for('auth.verify', action=action))

    return render_template('auth/phone_verification.html', title='Подтверждение номера телефона', verification_form=verification_form)

# Функция-представление страницы восстановления пароля
@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    reset_form = ResetPasswordForm()
    prev_page = request.args.get('prev', '')

    # Если на страницу изменения пароля пытаются зайти не через действие восстановление пароля,
    # то редиректим на главную страницу
    if not prev_page:
        return redirect(url_for('main.index'))

    if reset_form.validate_on_submit():
        user = User.query.filter_by(phone_number=session['phone_number'][2:]).first()
        user.set_password(reset_form.password.data)
        db.session.commit()
        session.pop('phone_number')

        # Если пользователь восстанавливает пароль из профиля, то разлогиниваем его
        if current_user.is_authenticated:
            logout_user()

        flash('Пароль успешно восстановлен', category='alert alert-success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Восстановление пароля', reset_form=reset_form)