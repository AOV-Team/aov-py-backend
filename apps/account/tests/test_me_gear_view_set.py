from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestMeGearViewSetGET(TestCase):
    """
    Test GET /api/me/gear
    """
    def test_me_gear_view_set_get_successful(self):
        """
        Test that we can get user's gear

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile = account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        gear = account_models.Gear(profile, [
            {
                'name': 'Canon T3i',
                'link': 'https://www.amazon.com/Canon-Digital-18-55mm-discontinued-manufacturer/dp/B004J3V90Y'
            },
            {
                'name': 'Tripod',
                'link': 'https://www.amazon.com/gp/product/B002FGTWOC/'
            }
        ])
        gear.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/gear')
        results = request.data

        self.assertEquals(len(results), 2)
        self.assertEquals(results[0]['name'], 'Canon T3i')

    def test_me_gear_view_set_get_empty(self):
        """
        Test that we get empty list if no gear

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/gear')
        results = request.data

        self.assertIsInstance(results, list)
        self.assertEquals(len(results), 0)

    def test_me_gear_view_set_get_no_profile(self):
        """
        Test that we get empty list even if no profile

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/gear')
        results = request.data

        self.assertIsInstance(results, list)
        self.assertEquals(len(results), 0)
