from django.conf import settings
from redis import StrictRedis
import random
import string

r = StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB['PASSWORD_CODES'])


def create_password_reset_code(user):
    """
    Create a password reset code for the given user

    :param user: User object
    :return: generated code
    """
    code = ''.join(random.choice(string.digits) for i in range(6))
    r.set(code, user.email)

    return code


def get_password_reset_email(code):
    """
    Look for code for given user and return email

    :param code: Code to get email for
    :return: email or None
    """
    email = r.get(code)

    if email:
        return email.decode('ascii')

    return None
