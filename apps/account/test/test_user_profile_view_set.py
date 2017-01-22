from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestUserProfileViewSetGET(TestCase):
    """
    Test /api/users/{}/profile
    """
    def test_user_profile_view_set_get_successful(self):
        """
        Test that we can get a user's profile

        :return: None
        """
        access_user = account_models.User.objects.create_user(email='m@mypapaya.io', password='pass', username='m')
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        account_models.Profile.objects.create_or_update(user=user, bio='This is a bio.')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/profile'.format(user.id))
        result = request.data

        self.assertIn('bio', result)
        self.assertIn('cover_image', result)
        self.assertNotIn('gear', result)

    def test_user_profile_view_set_get_no_profile(self):
        """
        Test that we get 404 if user has no profile

        :return: None
        """
        access_user = account_models.User.objects.create_user(email='m@mypapaya.io', password='pass', username='m')
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/profile'.format(user.id))

        self.assertEquals(request.status_code, 404)

    def test_user_profile_view_set_get_no_user(self):
        """
        Test that we get 404 if no user

        :return: None
        """
        access_user = account_models.User.objects.create_user(email='m@mypapaya.io', password='pass', username='m')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/profile'.format(99999))

        self.assertEquals(request.status_code, 404)

    def test_user_profile_view_set_get_own(self):
        """
        Test that user can get their own profile

        :return: None
        """
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        account_models.Profile.objects.create_or_update(user=user, bio='This is a bio.')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/profile'.format(user.id))
        result = request.data

        self.assertIn('bio', result)
        self.assertIn('cover_image', result)
        self.assertNotIn('gear', result)