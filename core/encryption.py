import jwt
from cryptography.fernet import Fernet
from student_portal import settings

CIPHER = Fernet(settings.SECRET_CIPHER_KEY)

def jwt_decode_handler(token):
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=['HS256']
    )

def jwt_encode_handler(payload):
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        'HS256'
    )

def crypto_encode(value):
    """
    It take value and makes one 100 character token
    :param value: any value
    :return: token
    """
    if value == '':
        raise ValueError('Please add some value!!')
    value = str.encode(str(value))
    return CIPHER.encrypt(value).decode('utf-8')

def crypto_decode(token):
    """
    It decode token to actual value
    :param token: token
    :return: it returns string value
    """
    if token == '':
        raise ValueError('Please add some value!!')
    token = str.encode(token)
    decrypted_text = CIPHER.decrypt(token)
    return decrypted_text.decode('utf-8')

def jwt_admin_payload_handler(admin):
    return {
        'ai': crypto_encode(admin.id),
        'bi': crypto_encode(admin.email),
    }
