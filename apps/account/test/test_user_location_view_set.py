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


class TestUsersViewSetGET(TestCase):
    """
    Test /api/users/{}/location GET (user location retrieval)
    """
    def test_user_location_view_set_get_successful(self):
        """
        Successful /api/users/{}/location GET.
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

        # Assert the POST worked, or else GET is guranteed to fail
        self.assertEqual(request.status_code, 200)

        response = client.get('/api/users/{}/location'.format(user.id), format='json')
        data = response.data

        self.assertEqual(response.status_code, 200)

        self.assertEqual(data["user"], user.id)
        self.assertEqual(data["location"], "Boise")
        self.assertEqual(data["latitude"], 43.6169233)
        self.assertEqual(data["longitude"], -116.2023436)

    def test_user_location_view_set_get_geo_location(self):
        """
        Test that we get users filtered by a box of coordinates

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
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

        # Assert the POST worked, or else GET is guranteed to fail
        self.assertEqual(request.status_code, 200)

        second_user = account_models.User.objects.create_user(
            email='mrtest2@mypapaya.io', password='WhoAmI', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(second_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            "location": "Boise",
            "geo_location": 'POINT ({} {})'.format(-116.2023436, 43.6169233)
        }

        request = client.post('/api/users/{}/location'.format(second_user.id), data=payload, format='json')

        # Assert the POST worked, or else GET is guranteed to fail
        self.assertEqual(request.status_code, 200)

        third_user = account_models.User.objects.create_user(
            email='mrtest2@mypapaya.io', password='WhoAmI', username='aov3')

        # Simulate auth
        token = test_helpers.get_token_for_user(third_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            "location": "Boise",
            "geo_location": 'POINT ({} {})'.format(-118.25, 45.61699)
        }

        request = client.post('/api/users/{}/location'.format(third_user.id), data=payload, format='json')

        # Assert the POST worked, or else GET is guranteed to fail
        self.assertEqual(request.status_code, 200)

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?geo_location=-118,42,-115,44')
        results = request.data['results']

        self.assertEquals(len(results), 2)
