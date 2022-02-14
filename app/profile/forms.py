from flask_wtf import FlaskForm
from flask_login import current_user
from app.models import User
from wtforms import StringField, IntegerField, PasswordField, TelField, SubmitField, SelectField
from wtforms import widgets
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
import email_validator

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

# Кастомное RadioField
class CustomRadioField(SelectField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.RadioInput()


    def pre_validate(self, form):
        if self.choices is None:
            raise TypeError(self.gettext("Choices cannot be None."))

        if not self.validate_choice:
            return

        # Если не была выбрана ни одна из кнопок, то не вызывает ошибку валидации
        for _, _, match in self.iter_choices():
            if match:
                break

# Кастомный валидатор email'а
class CustomEmailValidator(Email):

    def __call__(self, form, field):
        try:

            # Если поле с email пустое, то не вызывает ошибку валидации
            if not field.data:
                return

            email_validator.validate_email(
                field.data,
                check_deliverability=self.check_deliverability,
                allow_smtputf8=self.allow_smtputf8,
                allow_empty_local=self.allow_empty_local,
            )
        except email_validator.EmailNotValidError as e:
            message = self.message
            if message is None:
                if self.granular_message:
                    message = field.gettext(e)
                else:
                    message = field.gettext("Invalid email address.")
            raise ValidationError(message) from e

# Форма персональной информации в профиле
class InfoForm(FlaskForm):

    # С кастомным RadioField у пользователя есть возможность не указывать пол.
    # Поле не будет выдавать ошибку 'Not a valid choice' на превалидации
    # из-за того, что не был выбран ни один из вариантов
    sex = CustomRadioField('Пол', choices=['Мужской', 'Женский'], coerce=str)

    first_name = StringField('Имя', validators=[DataRequired(message=validaion_messages['data'])])
    phone_number = TelField('Телефон')

    # С кастомным валидатором у пользователя есть возможность не указывать email
    email = StringField('Email', validators=[CustomEmailValidator(message=validaion_messages['incorrect email'])])

    submit_info = SubmitField('Сохранить')

    # Функция-валидатор email'а перед его изменением в профиле.
    # Поднимает ошибку, если введенный email уже используется,
    # но пропустит текущий email пользователя для удобства
    # сохранения/обновления данных
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user != current_user:
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