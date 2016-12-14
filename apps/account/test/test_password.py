from apps.account import password
from apps.account import models as account_models
from django.conf import settings
from django.test import TestCase
import redis


class TestPassword(TestCase):
    def test_create_password_reset_code_successful(self):
        """
        Test that we can successfully create a reset code in Redis

        :return: None
        """
        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')
        code = password.create_password_reset_code(user)

        # Check that there's a code
        r = redis.StrictRedis(host='localhost', port=settings.REDIS_PORT, db=settings.REDIS_DB['PASSWORD_CODES'])

        self.assertIsNotNone(r.get(user.email))
        self.assertEquals(code, r.get(user.email).decode('ascii'))
