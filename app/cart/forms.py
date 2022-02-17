from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, SelectField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length

validaion_messages = {
    'data': 'Поле обязательно для заполнения',
    'length': 'Длина сообщения должна быть не более 256 символов'
}

class OrderForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(message=validaion_messages['data'])])
    phone_number = StringField('Номер телефона', validators=[DataRequired(message=validaion_messages['data'])])
    addresses = SelectField('Адрес доставки', choices=[(0, 'Указать новый адрес')], validate_choice=False)
    street = StringField('Улица', validators=[DataRequired(message=validaion_messages['data'])])
    house = StringField('Дом', validators=[DataRequired(message=validaion_messages['data'])])
    building = StringField('Корпус')
    entrance = StringField('Подъезд')
    floor = StringField('Этаж')
    apartment = StringField('Квартира')
    additional_info = StringField('Дополнительная информация')
    date = SelectField('Дата', choices=[])
    time = SelectField('Время', choices=[], validate_choice=False)
    payment_method = RadioField('Способ оплаты', choices=['Наличными курьеру', 'Картой курьеру'])
    number_of_persons = SelectField('Количество персон', choices=[f'{i} человек(а)' for i in range(1, 11)])
    order_notes = TextAreaField('Примечания к заказу', validators=[Length(max=256, message=validaion_messages['length'])])
    submit_order = SubmitField('Оформить заказ')