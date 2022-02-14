from flask import current_app
from twilio.rest import Client, TwilioException

def _get_twilio_verify_client():
    return Client(
        current_app.config['TWILIO_ACCOUNT_SID'],
        current_app.config['TWILIO_AUTH_TOKEN']
    )

def request_verification_token(phone_number):
    '''
    Функция принимает номер телефона в формате "+79991234567" и высылает sms
    с токеном верификации. Если возникает ошибка, то бот сообщит токен через звонок

        Параметры:
                    phone_humber (str): Номер телефона в формате "+79991234567"

        Возвращаемое значание:
                    None
    '''
    verify = _get_twilio_verify_client().verify.services(current_app.config['TWILIO_VERIFY_SERVICE_ID'])
    try:
        verify.verifications.create(to=phone_number, channel='sms')
    except TwilioException:
        verify.verifications.create(to=phone_number, channel='call')

# Проверяет валидность введенного кода
def check_verification_token(phone_number, token):
    '''
    Функция принимает номер телефона в формате "+79991234567" и токен верификации,
    и проверяет его валидность

        Параметры:
                    phone_humber (str): Номер телефона в формате "+79991234567"
                    token (str): Токен верификации

        Возвращаемое значание:
                    result (bool): True, если токен валидный, False - если возникает исключение
    '''
    verify = _get_twilio_verify_client().verify.services(current_app.config['TWILIO_VERIFY_SERVICE_ID'])
    try:
        result = verify.verification_checks.create(to=phone_number, code=token)
    except TwilioException:
        return False
    return result.status == 'approved'

def parse_phone_number(phone_humber):
    '''
    Функция принимает номер телефона из полей форм в формате "+7 999 123-45-67"
    и возвращает его в формате "+79991234567"

        Параметры:
                    phone_humber (str): Номер телефона в формате "+7 999 123-45-67"

        Возвращаемое значание:
                    phone_humber (str): Номер телефона в формате "+79991234567"
    '''
    phone_humber = phone_humber.replace(' ', '').replace('-', '')
    return phone_humber