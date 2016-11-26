from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestMeProfileViewSetGET(TestCase):
    """
    Test GET /api/me/profile
    """
    def test_me_profile_view_set_get_successful(self):
        """
        Test that we can get user's profile

        :return: None
        """
        # Create user and data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/profile')
        result = request.data['result']

        self.assertIn('bio', result)
        self.assertIn('cover_image', result)
        self.assertIn('gear', result)

    def test_me_profile_view_set_get_does_not_exist(self):
        """
        Test that we get 404 if user does not have a profile

        :return: None
        """
        # Create user
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/profile')

        self.assertEquals(request.status_code, 404)
