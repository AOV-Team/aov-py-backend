from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestUsersViewSetPOST(TestCase):
    """
    Test /api/users/{}/location POST (user location creation)
    """
    def test_user_location_view_set_post_successful(self):
        """
        Successful /api/users/{}/location POST.
        Log user in to make sure password is correctly set

        :return: None
        """
        user_data = {
            'email': 'mr@mypapaya.io',
            'password': 'WhoWantsToBeAMillionaire?',
            'username': 'aov_hov'
        }
        user = account_models.User.objects.create_user(**user_data)

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            "location": "Boise",
            "geo_location": 'POINT ({} {})'.format(-116.2023436, 43.6169233)
        }

        request = client.post('/api/users/{}/location'.format(user.id), data=payload, format='json')
        result = request.data

        self.assertIn('coordinates', result)
        self.assertIn('latitude', result)
        self.assertIn('location', result)
        self.assertIn('longitude', result)
        self.assertIn('user', result)
        self.assertEqual(result['latitude'], 43.6169233)
        self.assertEqual(result['location'], 'Boise')
        self.assertEqual(result['longitude'], -116.2023436)
