from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestUserSingleViewSet(TestCase):
    """
    Test /api/users/{}
    """
    def test_user_single_view_set_successful(self):
        """
        Test that we can get user data

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io', first_name='Martin',
                                                       last_name='Ronquillo', location='Boise',
                                                       social_name='@ronquilloaeon', password='pass',
                                                       username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}'.format(user.id), format='json')
        result = request.data

        self.assertEquals(result['id'], user.id)
        self.assertEquals(result['age'], user.age)
        self.assertEquals(result['first_name'], user.first_name)
        self.assertEquals(result['last_name'], user.last_name)
        self.assertEquals(result['location'], user.location)
        self.assertEquals(result['social_name'], user.social_name)
        self.assertEquals(result['username'], user.username)

    def test_user_single_view_set_inactive(self):
        """
        Test that we can HTTP 404 if user is not active

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        user_2 = account_models.User.objects.create_user(email='mr2test@mypapaya.io', is_active=False, password='pass',
                                                         username='aov_hovy')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}'.format(user_2.id), format='json')

        self.assertEquals(request.status_code, 404)

    def test_user_single_view_set_not_found(self):
        """
        Test that we can HTTP 404 if user is not found

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}'.format(555555), format='json')

        self.assertEquals(request.status_code, 404)
