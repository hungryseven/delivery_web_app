from flask import current_app
from twilio.rest import Client, TwilioException

def _get_twilio_verify_client():
    return Client(
        current_app.config['TWILIO_ACCOUNT_SID'],
        current_app.config['TWILIO_AUTH_TOKEN']
    )

# Сначала запрашивает отправку кода по sms,
# при неудаче - в качестве голосового сообщения
def request_verification_token(phone_number):
    verify = _get_twilio_verify_client().verify.services(current_app.config['TWILIO_VERIFY_SERVICE_ID'])
    try:
        verify.verifications.create(to=phone_number, channel='sms')
    except TwilioException:
        verify.verifications.create(to=phone_number, channel='call')

# Проверяет валидность введенного кода
def check_verification_token(phone_number, token):
    verify = _get_twilio_verify_client().verify.services(current_app.config['TWILIO_VERIFY_SERVICE_ID'])
    try:
        result = verify.verification_checks.create(to=phone_number, code=token)
    except TwilioException:
        return False
    return result.status == 'approved'

# Возвращает номер телефона в формате '+79991234567'
def parse_phone_number(phone_humber):
    phone_humber = phone_humber.replace(' ', '').replace('-', '')
    return phone_humber