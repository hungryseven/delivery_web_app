from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TelField, SelectField, RadioField
from wtforms.validators import DataRequired

validaion_messages = {
    'data': 'Поле обязательно для заполнения'
}

class OrderForm(FlaskForm):
    address = RadioField('Адрес доставки', choices=[])
    street = StringField('Улица', validators=[DataRequired(message=validaion_messages['data'])])
    house = StringField('Дом', validators=[DataRequired(message=validaion_messages['data'])])
    building = StringField('Корпус')
    entrance = StringField('Подъезд')
    floor = StringField('Этаж')
    apartment = StringField('Квартира')
    additional_info = StringField('Дополнительная информация')