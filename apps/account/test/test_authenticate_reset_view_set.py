from apps.account import models as account_models
from apps.account import password
from django.conf import settings
from django.core import mail
from django.test import TestCase
from rest_framework.test import APIClient
import redis


class TestAuthenticateResetViewSetPATCH(TestCase):
    """
    Test that we can reset password
    """

    def setUp(self):
        self.r = redis.StrictRedis(host='localhost', port=settings.REDIS_PORT, db=settings.REDIS_DB['PASSWORD_CODES'])

    def tearDown(self):
        self.r.flushdb()

    def test_authenticate_reset_view_set_patch_successful(self):
        """
        Test that we can successfully reset user's password

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')
        code = password.create_password_reset_code(user)

        client = APIClient()

        payload = {
            'code': code,
            'password': 'aaa'
        }

        request = client.patch('/api/auth/reset', data=payload, format='json')

        self.assertEquals(request.status_code, 200)

        # Check that we can authenticate w/ new password
        login_request = client.post('/api/auth', data={'email': 'test@test.com', 'password': 'aaa'}, format='json')

        self.assertEquals(login_request.status_code, 201)
        self.assertIn('token', login_request.data)

    def test_authenticate_reset_view_set_patch_bad_code(self):
        """
        Test that we get 403 if code is incorrect

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')
        code = password.create_password_reset_code(user)

        client = APIClient()

        payload = {
            'code': code + 'fail',
            'password': 'aaa'
        }

        request = client.patch('/api/auth/reset', data=payload, format='json')

        self.assertEquals(request.status_code, 403)

        # Check that we cannot authenticate w/ new password
        login_request = client.post('/api/auth', data={'email': 'test@test.com', 'password': 'aaa'}, format='json')

        self.assertEquals(login_request.status_code, 401)

    def test_authenticate_reset_view_set_patch_different_case(self):
        """
        Test that we can successfully reset user's password even if provided case is different than what's saved

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='Spencer.a.marsh@gmail.com', username='aov1')
        code = password.create_password_reset_code(user)

        client = APIClient()

        payload = {
            'code': code,
            'password': 'aaa'
        }

        request = client.patch('/api/auth/reset', data=payload, format='json')

        self.assertEquals(request.status_code, 200)

        # Check that we can authenticate w/ new password
        login_request = client.post('/api/auth', data={'email': 'spencer.a.marsh@gmail.com', 'password': 'aaa'},
                                    format='json')

        self.assertEquals(login_request.status_code, 201)
        self.assertIn('token', login_request.data)

    def test_authenticate_reset_view_set_patch_no_code(self):
        """
        Test that we get 403 if no code exists for user

        :return: None
        """
        # Create test data
        account_models.User.objects.create_user(email='test@test.com', username='aov1')

        client = APIClient()

        payload = {
            'code': 'fail',
            'password': 'aaa'
        }

        request = client.patch('/api/auth/reset', data=payload, format='json')

        self.assertEquals(request.status_code, 403)

        # Check that we cannot authenticate w/ new password
        login_request = client.post('/api/auth', data={'email': 'test@test.com', 'password': 'aaa'}, format='json')

        self.assertEquals(login_request.status_code, 401)

    def test_authenticate_reset_view_set_patch_no_user(self):
        """
        Test that we get 404 if user no longer exists

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='test123@test.com', username='aov12')
        code = password.create_password_reset_code(user)

        # Delete user
        user.delete()

        # Check that user does not exist
        users = account_models.User.objects.filter(email=user.email)

        self.assertEquals(len(users), 0)

        # Try to set password
        client = APIClient()

        payload = {
            'code': code,
            'password': 'aaa'
        }

        request = client.patch('/api/auth/reset', data=payload, format='json')

        self.assertEquals(request.status_code, 404)


class TestAuthenticateResetViewSetPOST(TestCase):
    """
    Test that we can request to reset password

    """

    def setUp(self):
        self.r = redis.StrictRedis(host='localhost', port=settings.REDIS_PORT, db=settings.REDIS_DB['PASSWORD_CODES'])

    def tearDown(self):
        self.r.flushdb()

    def test_authenticate_reset_view_set_post_successful(self):
        """
        Test that we can successfully request code for resetting user's password

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')

        client = APIClient()

        payload = {
            'email': user.email
        }

        request = client.post('/api/auth/reset', data=payload, format='json')

        self.assertEquals(request.status_code, 201)

        # Check that an email was sent
        self.assertEquals(len(mail.outbox), 1)

    def test_authenticate_reset_view_set_post_already_requested(self):
        """
        Test that if code already exists for a user, another email is sent out

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')
        code = password.create_password_reset_code(user)

        client = APIClient()

        payload = {
            'email': user.email
        }

        request = client.post('/api/auth/reset', data=payload, format='json')

        self.assertEquals(request.status_code, 201)

        # Check that an email was sent
        self.assertEquals(len(mail.outbox), 1)

    def test_authenticate_reset_view_set_post_different_case(self):
        """
        Test that we can successfully request code for resetting user's password even if they request it with an email
        that has different case than what's saved in the db

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='Spencer.a.marsh@gmail.com', username='aov1')

        client = APIClient()

        payload = {
            'email': user.email.lower()
        }

        request = client.post('/api/auth/reset', data=payload, format='json')

        self.assertEquals(request.status_code, 201)

        # Check that an email was sent
        self.assertEquals(len(mail.outbox), 1)

    def test_authenticate_reset_view_set_post_no_email(self):
        """
        Test that we can get 400 if email not provided

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')

        client = APIClient()
        request = client.post('/api/auth/reset', data={}, format='json')

        self.assertEquals(request.status_code, 400)

        # Check that user has no code
        self.assertIsNone(self.r.get(user.email))

        # Check that an email was sent
        self.assertEquals(len(mail.outbox), 0)

    def test_authenticate_reset_view_set_post_no_user(self):
        """
        Test that we get 200 even if user does not exist

        :return: None
        """
        client = APIClient()

        payload = {
            'email': 'fake@test.com'
        }

        request = client.post('/api/auth/reset', data=payload, format='json')

        self.assertEquals(request.status_code, 201)

        # Check that code is different
        self.assertIsNone(self.r.get('fake@test.com'))

        # Check that an email was sent
        self.assertEquals(len(mail.outbox), 0)
