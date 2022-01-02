from flask_wtf import FlaskForm
from flask_login import current_user
from app.models import User
from wtforms import StringField, PasswordField, TelField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError

validaion_messages = {
    'data': 'Поле обязательно для заполнения',
    'incorrect email': 'Неверный формат электронной почты',
    'not equal': 'Пароли не совпадают',
    'incorrect password': 'Неверный формат пароля',
    'length': 'Пароль должен содержать минимум 8 символов',
    'email not available': 'Введенный адрес электронной почты уже используется',
    'phone not available': 'Введенный номер телефона уже используется'
}

class InfoForm(FlaskForm):
    sex = RadioField('Пол', choices=['Мужской', 'Женский'], coerce=str)
    first_name = StringField('Имя', validators=[DataRequired(message=validaion_messages['data'])])
    phone_number = TelField('Телефон', validators=[])
    email = StringField('Email', validators=[Email(message=validaion_messages['incorrect email'])])
    submit_info = SubmitField('Сохранить')

    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user is not None and user != current_user and phone_number.data != '':
            raise ValidationError(validaion_messages['phone not available'])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user != current_user:
            raise ValidationError(validaion_messages['email not available'])

class PasswordForm(FlaskForm):
    current_password = PasswordField(
        'Текущий пароль', validators=[DataRequired(message=validaion_messages['data'])])
    new_password = PasswordField(
        'Новый пароль', validators=[DataRequired(message=validaion_messages['data']),
                                    Length(min=8, max=20, message=validaion_messages['length']),
                                    Regexp('^(?=.*[0-9])(?=.*[a-zA-Z])(?=\S+$).{1,}$', message=validaion_messages['incorrect password'])])
    new_password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(message=validaion_messages['data']),
                                        EqualTo('new_password', message=validaion_messages['not equal'])])
    submit_password = SubmitField('Сохранить')