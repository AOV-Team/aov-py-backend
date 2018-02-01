from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestUserSearchViewSet(TestCase):
    """
    Test /api/users/search
    """
    def test_user_search_view_set_first_name_successful(self):
        """
        Test that searching by first name works successfully

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io', first_name='Martin',
                                                       last_name='Ronquillo', location='Boise',
                                                       social_name='@ronquilloaeon', password='pass',
                                                       username='aov_hov')

        account_models.User.objects.create_user(age=25, email='gallen@mypapaya.io', first_name='Garrett',
                                                last_name='Allen', location='Boise',
                                                social_name='@neelik', password='pass',
                                                username='aov_neelik')


        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/search/users?q=Martin', format='json')
        result = request.data

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"][0]["id"], user.id)

    def test_user_search_view_set_last_name_successful(self):
        """
            Unit test to see that searching by last name works

        :return: No return
        """
        # Create test data
        user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io', first_name='Martin',
                                                       last_name='Ronquillo', location='Boise',
                                                       social_name='@ronquilloaeon', password='pass',
                                                       username='aov_hov')

        other_user = account_models.User.objects.create_user(age=25, email='gallen@mypapaya.io', first_name='Garrett',
                                                             last_name='Allen', location='Boise',
                                                             social_name='@neelik', password='pass',
                                                             username='aov_neelik')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/search/users?q=Allen', format='json')
        result = request.data

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"][0]["id"], other_user.id)

    def test_user_search_view_set_username_successful(self):
        """
            Unit test to see that searching by username works

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io', first_name='Martin',
                                                       last_name='Ronquillo', location='Boise',
                                                       social_name='@ronquilloaeon', password='pass',
                                                       username='aov_hov')

        account_models.User.objects.create_user(age=25, email='gallen@mypapaya.io', first_name='Garrett',
                                                last_name='Allen', location='Boise',
                                                social_name='@neelik', password='pass',
                                                username='aov_neelik')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/search/users?q=aov', format='json')
        result = request.data

        self.assertEqual(result["count"], 2)

    def test_user_search_view_set_social_name_successful(self):
        """
            Unit test for searching by social name

        :return: No return
        """

        # Create test data
        user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io', first_name='Martin',
                                                       last_name='Ronquillo', location='Boise',
                                                       social_name='@ronquilloaeon', password='pass',
                                                       username='aov_hov')

        other_user = account_models.User.objects.create_user(age=25, email='gallen@mypapaya.io', first_name='Garrett',
                                                             last_name='Allen', location='Boise',
                                                             social_name='@neelik', password='pass',
                                                             username='aov_dev')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/search/users?q=neelik', format='json')
        result = request.data

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"][0]["id"], other_user.id)
