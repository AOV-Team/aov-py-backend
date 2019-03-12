from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestAOVWebUserProfileGET(TestCase):
    """
    Test /api/aov-web/users/{}/profile
    """
    def test_aov_web_user_profile_view_get_successful(self):
        """
        Test that we can get a user's profile

        :return: None
        """
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        account_models.Profile.objects.create_or_update(user=user, bio='This is a bio.')

        request = APIClient().get('/api/aov-web/users/{}/profile'.format(user.id))
        result = request.data["results"][0]

        self.assertIn('bio', result)
        self.assertIn('cover_image', result)

    def test_user_profile_view_set_get_no_profile(self):
        """
        Test that we get 404 if user has no profile

        :return: None
        """
        request = APIClient().get('/api/aov-web/users/999999999/profile')

        self.assertEquals(len(request.data["results"]), 0)
