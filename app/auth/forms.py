from flask_wtf import FlaskForm
from app.models import User
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError

validaion_messages = {
    'data': 'Поле обязательно для заполнения',
    'incorrect email': 'Неверный формат электронной почты',
    'not equal': 'Пароли не совпадают',
    'incorrect password': 'Неверный формат пароля',
    'length': 'Пароль должен содержать минимум 8 символов',
    'email not available': 'Введенный адрес электронной почты уже используется'
}

class LoginForm(FlaskForm):
    email = StringField(
        'Email', validators=[DataRequired(message=validaion_messages['data']),
                            Email(message=validaion_messages['incorrect email'])])
    password = PasswordField('Пароль', validators=[DataRequired(message=validaion_messages['data'])])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(message=validaion_messages['data'])])
    email = StringField(
        'Email', validators=[DataRequired(message=validaion_messages['data']),
                            Email(message=validaion_messages['incorrect email'])])
    password = PasswordField(
        'Пароль', validators=[DataRequired(message=validaion_messages['data']),
                            Length(min=8, max=20, message=validaion_messages['length']),
                            Regexp('^(?=.*[0-9])(?=.*[a-zA-Z])(?=\S+$).{1,}$', message=validaion_messages['incorrect password'])])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(message=validaion_messages['data']),
                                        EqualTo('password', message=validaion_messages['not equal'])])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(validaion_messages['email not available'])