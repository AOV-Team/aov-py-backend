from apps.account import authenticate
from apps.account import models as account_models
from django.conf import settings
from django.test import TestCase
import redis
import time


class TestAuthenticate(TestCase):
    def setUp(self):
        self.r = redis.StrictRedis(host='localhost', port=settings.REDIS_PORT, db=settings.REDIS_DB['AUTHENTICATION_CODES'])

    def tearDown(self):
        self.r.flushdb()

    def test_authenticate_create_authentication_code_successful(self):
        """
        Test that we can successfully create an authentication code in Redis

        :return: None
        """

        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')
        code = authenticate.create_authentication_code(user)

        # Check that there's a code
        self.assertIsNotNone(self.r.get(code))
        self.assertEquals(user.email, self.r.get(code).decode('ascii'))

    def test_get_authenticating_email_successful(self):
        """
        Test that we can get email

        :return: None
        """
        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')
        code = authenticate.create_authentication_code(user)
        email = authenticate.get_authenticating_email(code)

        self.assertEquals(user.email, email)

    def test_get_authentication_code_none(self):
        """
        Test that we get None if no code for user

        :return: None
        """
        account_models.User.objects.create_user(email='test@test.com', username='aov1')
        email = authenticate.get_authenticating_email('fffstg')

        self.assertIsNone(email)

    def test_delete_authentication_code_successful(self):
        """
        Test that deleting the code works properly

        :return: None
        """

        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')
        code = authenticate.create_authentication_code(user)
        email = authenticate.get_authenticating_email(code)

        self.assertIsNotNone(email)

        authenticate.delete_authentication_code(code)

        self.assertFalse(self.r.exists(code))

    def test_delete_authentication_code_no_code(self):
        """
        Test a False is returned if the code doesn't have a matching Redis entry
        :return: None
        """

        deleted = authenticate.delete_authentication_code('Nonsense')

        self.assertFalse(deleted)
