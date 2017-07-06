from django.conf import settings
from redis import StrictRedis
import uuid

redis_db = StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB['AUTHENTICATION_CODES'],
                password=settings.REDIS_PASSWORD)


def create_authentication_code(user):
    """
    Create an authentication code for the given user

    :param user: User object
    :return: generated code
    """
    code = uuid.uuid4()
    redis_db.set(code, user.email)

    return code

def delete_authentication_code(code):
    """
        Delete an existing entry with the used code
    :param code: Authentication code
    :return: None
    """

    redis_db.delete(code)

def get_authenticating_email(code):
    """
    Look for email associated to the given code and return it

    :param code: Code to get email for
    :return: email or None
    """
    email = redis_db.get(code)

    if email:
        return email.decode('ascii')

    return None