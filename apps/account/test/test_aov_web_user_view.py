from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestAOVWebUserViewGET(TestCase):
    """
    Test /api/users/{}
    """
    def test_aov_web_user_view_get_successful(self):
        """
        Test that we can get user data

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io', first_name='Martin',
                                                       last_name='Ronquillo', location='Boise',
                                                       social_name='@ronquilloaeon', password='pass',
                                                       username='aov_hov')

        request = APIClient().get('/api/aov-web/users/{}'.format(user.id), format='json')
        result = request.data["results"][0]

        self.assertEquals(result['id'], user.id)
        self.assertEquals(result['age'], user.age)
        self.assertEquals(result['first_name'], user.first_name)
        self.assertEquals(result['last_name'], user.last_name)
        self.assertEquals(result['location'], user.location)
        self.assertEquals(result['social_name'], user.social_name)
        self.assertEquals(result['username'], user.username)
        self.assertIn("avatar", result)

    def test_aov_web_user_view_get_not_found(self):
        """
        Test that we can HTTP 404 if user is not found

        :return: None
        """
        # Get data from endpoint
        client = APIClient()

        request = client.get('/api/aov-web/users/{}'.format(555555), format='json')

        self.assertEquals(len(request.data["results"]), 0)
