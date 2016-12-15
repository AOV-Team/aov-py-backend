from apps.account import password
from apps.account import models as account_models
from django.conf import settings
from django.test import TestCase
import redis


class TestPassword(TestCase):
    def setUp(self):
        self.r = redis.StrictRedis(host='localhost', port=settings.REDIS_PORT, db=settings.REDIS_DB['PASSWORD_CODES'])

    def tearDown(self):
        self.r.flushdb()

    def test_create_password_reset_code_successful(self):
        """
        Test that we can successfully create a reset code in Redis

        :return: None
        """
        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')
        code = password.create_password_reset_code(user)

        # Check that there's a code
        self.assertIsNotNone(self.r.get(code))
        self.assertEquals(user.email, self.r.get(code).decode('ascii'))

    def test_get_password_reset_email_successful(self):
        """
        Test that we can get email

        :return: None
        """
        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')
        code = password.create_password_reset_code(user)
        email = password.get_password_reset_email(code)

        self.assertEquals(user.email, email)

    def test_get_password_reset_code_none(self):
        """
        Test that we get None if no code for user

        :return: None
        """
        account_models.User.objects.create_user(email='test@test.com', username='aov1')
        email = password.get_password_reset_email('fffstg')

        self.assertIsNone(email)
