from flask_wtf import FlaskForm
from app.models import User
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp, ValidationError
from app.auth.phone_verification import parse_phone_number

validaion_messages = {
    'data': 'Поле обязательно для заполнения',
    'incorrect email': 'Неверный формат электронной почты',
    'not equal': 'Пароли не совпадают',
    'incorrect password': 'Неверный формат пароля',
    'length': 'Пароль должен содержать минимум 8 символов',
    'phone not available': 'Введенный номер телефона уже используется'
}

# Форма для авторизации
class LoginForm(FlaskForm):
    phone_number = StringField('Номер телефона', validators=[DataRequired(message=validaion_messages['data'])])
    password = PasswordField('Пароль', validators=[DataRequired(message=validaion_messages['data'])])
    remember_me = BooleanField('Запомнить меня')
    submit_login = SubmitField('Войти')

# Форма для регистрации
class RegisterForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(message=validaion_messages['data'])])
    phone_number = StringField('Номер телефона', validators=[DataRequired(message=validaion_messages['data'])])
    password = PasswordField(
        'Пароль', validators=[DataRequired(message=validaion_messages['data']),
                            Length(min=8, max=20, message=validaion_messages['length']),
                            Regexp('^(?=.*[0-9])(?=.*[a-zA-Z])(?=\S+$).{1,}$', message=validaion_messages['incorrect password'])])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(message=validaion_messages['data']),
                                        EqualTo('password', message=validaion_messages['not equal'])])
    submit_register = SubmitField('Зарегистрироваться')

    # Функция-валидатор номера телефона при регистрации. Поднимает исключение,
    # если пользователь с введенным номером телефона уже зарегистрирован
    def validate_phone_number(self, phone_number):
        phone_number = parse_phone_number(phone_number.data)[2:]
        user = User.query.filter_by(phone_number=phone_number).first()
        if user is not None:
            raise ValidationError(validaion_messages['phone not available'])

# Форма для подтверждения номера телефона
class VerificationForm(FlaskForm):
    code = StringField('Код', validators=[DataRequired(message=validaion_messages['data'])])
    submit_code = SubmitField('Подтвердить')

# Форма запроса номера телефона для восстановления пароля
class PhoneRequestForm(FlaskForm):
    requested_phone = StringField('Номер телефона', validators=[DataRequired(message=validaion_messages['data'])])
    submit_phone_number = SubmitField('Отправить код')

# Форма для восстановления пароля
class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'Пароль', validators=[DataRequired(message=validaion_messages['data']),
                            Length(min=8, max=20, message=validaion_messages['length']),
                            Regexp('^(?=.*[0-9])(?=.*[a-zA-Z])(?=\S+$).{1,}$', message=validaion_messages['incorrect password'])])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(message=validaion_messages['data']),
                                        EqualTo('password', message=validaion_messages['not equal'])])
    submit_password = SubmitField('Сохранить')


