from flask_wtf import FlaskForm
from flask_login import current_user
from app.models import User
from wtforms import StringField, IntegerField, PasswordField, TelField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError

validaion_messages = {
    'data': 'Поле обязательно для заполнения',
    'length': 'Пароль должен содержать минимум 8 символов',
    'not equal': 'Пароли не совпадают',
    'incorrect password': 'Неверный формат пароля',
    'incorrect email': 'Неверный формат электронной почты',
    'incorrect phone': 'Неверный формат номера телефона',
    'email not available': 'Введенный адрес электронной почты уже используется',
    'phone not available': 'Введенный номер телефона уже используется'
}

# Форма персональной информации в профиле
class InfoForm(FlaskForm):
    sex = RadioField('Пол', choices=['Мужской', 'Женский'], coerce=str)
    first_name = StringField('Имя', validators=[DataRequired(message=validaion_messages['data'])])
    phone_number = TelField('Телефон')
    email = StringField('Email', validators=[Email(message=validaion_messages['incorrect email'])])
    submit_info = SubmitField('Сохранить')

    # Функция-валидатор email'а перед его изменением в профиле.
    # Поднимает ошибку, если введенный email уже используется,
    # но пропустит текущий email пользователя для удобства
    # сохранения/обновления данных
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user != current_user and current_user.email != '':
            raise ValidationError(validaion_messages['email not available'])

# Форма изменения пароля в профиле
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

# Форма для добавления, редактирования и удаления адресов пользователей.
# Атрибут 'address_id' необходим для скрытого поля в форме для того,
# чтобы вытащить нужный адрес из БД для редактирования
class AddressForm(FlaskForm):
    address_id = IntegerField('ID адреса')
    street = StringField('Улица', validators=[DataRequired(message=validaion_messages['data'])])
    house = StringField('Дом', validators=[DataRequired(message=validaion_messages['data'])])
    building = StringField('Корпус')
    entrance = StringField('Подъезд')
    floor = StringField('Этаж')
    apartment = StringField('Квартира')
    additional_info = StringField('Дополнительная информация')
    submit_address = SubmitField('Сохранить')
    edit_address = SubmitField('Сохранить')