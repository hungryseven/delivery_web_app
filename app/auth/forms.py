from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

validaion_messages = {
    'data': 'Поле обязательно для заполнения',
    'email': 'Неверный формат электронной почты',
    'not equal': 'Пароли не совпадают',
    'length': 'Пароль должен содержать минимум 8 символов'
}

class LoginForm(FlaskForm):
    email = StringField(
        'Email', validators=[DataRequired(message=validaion_messages['data']),
                            Email(message=validaion_messages['email'])])
    password = PasswordField('Пароль', validators=[DataRequired(message=validaion_messages['data'])])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(message=validaion_messages['data'])])
    email = StringField(
        'Email', validators=[DataRequired(message=validaion_messages['data']),
                            Email(message=validaion_messages['email'])])
    password = PasswordField(
        'Пароль', validators=[DataRequired(message=validaion_messages['data']),
                            Length(min=8, max=20, message=validaion_messages['length'])])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(message=validaion_messages['data']),
                                        EqualTo('password', message=validaion_messages['not equal'])])
    submit = SubmitField('Зарегистрироваться')