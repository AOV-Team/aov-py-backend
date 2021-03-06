from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from unittest import skip


class TestAuthenticateViewSetDELETE(TestCase):
    def test_authenticate_view_set_delete_successful(self):
        """
        Test that we can log a user out

        :return: None
        """
        # Create a user
        user = account_models.User.objects.create_user(email='test@test.com', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/auth')

        self.assertEquals(request.status_code, 200)

        tokens = Token.objects.all()

        self.assertEquals(len(tokens), 0)

    def test_authenticate_view_set_delete_user_not_authenticated(self):
        """
        Test that we get a HTTP 401 status code if user not logged in

        :return: None
        """
        # Create a user
        account_models.User.objects.create_user(email='test@test.com', username='aov1')

        # Get data from endpoint
        client = APIClient()

        request = client.delete('/api/auth')
        self.assertEquals(request.status_code, 401)


class TestAuthViewSetPOST(TestCase):
    """
    Test endpoint to log user in
    """
    def test_authenticate_view_set_post_successful(self):
        """
        /api/auth POST

        :return: None
        """
        # Create user
        account_models.User.objects\
            .create_user(email='mrtest@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov1')

        # Log user in
        client = APIClient()

        payload = {
            'email': 'mrtest@mypapaya.io',
            'password': 'WhoWantsToBeAMillionaire?'
        }

        request = client.post('/api/auth', data=payload, format='json')
        response = request.data

        self.assertIsNotNone(response['token'])

    def test_authenticate_view_set_post_case_insensitive(self):
        """
        /api/auth POST - test that email is case insensitive

        :return: None
        """
        # Create user
        account_models.User.objects\
            .create_user(email='mrtest@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov1')

        # Log user in
        client = APIClient()

        payload = {
            'email': 'MRtest@mypapaya.io',
            'password': 'WhoWantsToBeAMillionaire?'
        }

        request = client.post('/api/auth', data=payload, format='json')
        response = request.data

        self.assertIsNotNone(response['token'])

    def test_authenticate_view_set_post_case_insensitive_2_accounts(self):
        """
        /api/auth POST - test that if there are two email accounts that are the same but different case,
        it authenticates to the first one that matches the password

        :return: None
        """
        # Create users
        user = account_models.User.objects\
            .create_user(email='mrtest@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov1')

        account_models.User.objects \
            .create_user(email='MRtest@mypapaya.io', password='WhosAMillionaire', username='aov2')

        # Log user in
        client = APIClient()

        payload = {
            'email': 'MRtest@mypapaya.io',
            'password': 'WhoWantsToBeAMillionaire?'
        }

        request = client.post('/api/auth', data=payload, format='json')
        response = request.data
        token = response['token']

        self.assertIsNotNone(token)

        # Get user data
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        me_request = client.get('/api/me', format='json')
        me_result = me_request.data

        self.assertEquals(me_result['id'], user.id)

    def test_authenticate_view_set_post_different_case(self):
        """
        /api/auth POST - test that email is case insensitive - for emails that got transferred from old backend

        :return: None
        """
        # Create user
        account_models.User.objects\
            .create_user(email='Spencer.a.marsh@gmail.com', password='WhoWantsToBeAMillionaire?', username='aov1')

        # Log user in
        client = APIClient()

        payload = {
            'email': 'spencer.a.marsh@gmail.com',
            'password': 'WhoWantsToBeAMillionaire?'
        }

        request = client.post('/api/auth', data=payload, format='json')
        response = request.data

        self.assertIsNotNone(response['token'])

    def test_authenticate_view_set_post_bad_request(self):
        """
        Test that we get a HTTP 400 code if email and/or password missing in payload

        :return: None
        """
        # Create user
        account_models.User.objects\
            .create_user(email='mrtest@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov1')

        # Log user in
        client = APIClient()

        payload = {
            'email': 'mrtest@mypapaya.io',
        }

        request = client.post('/api/auth', data=payload, format='json')
        self.assertEquals(request.status_code, 400)

    @skip('Cannot deactivate user for some reason')
    def test_authenticate_view_set_post_inactive_user(self):
        """
        Test that we get a HTTP 403 if user is not active

        :return: None
        """
        # Create user
        user = account_models.User.objects\
            .create_user(email='mrtest@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov1')
        user.is_active = False
        user.save()

        # Log user in
        client = APIClient()

        payload = {
            'email': 'mrtest@mypapaya.io',
            'password': 'WhoWantsToBeAMillionaire?'
        }

        request = client.post('/api/auth', data=payload, format='json')
        self.assertEquals(request.status_code, 403)

    def test_authenticate_view_set_post_incorrect_credentials(self):
        """
        Verify that we get a HTTP 401 code if authentication fails

        :return: None
        """
        # Create user
        account_models.User.objects\
            .create_user(email='mrtest@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov1')

        # Log user in
        client = APIClient()

        payload = {
            'email': 'mrtest@mypapaya.io',
            'password': 'Me!'
        }

        request = client.post('/api/auth', data=payload, format='json')
        self.assertEquals(request.status_code, 401)

    def test_authenticate_view_set_user_post_does_not_exist(self):
        """
        Verify that we get a HTTP 401 code if user does not exist

        :return: None
        """
        client = APIClient()

        payload = {
            'email': 'mrtest@mypapaya.io',
            'password': 'Me!'
        }

        request = client.post('/api/auth', data=payload, format='json')
        self.assertEquals(request.status_code, 401)
