from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestMeViewSetGET(TestCase):
    """
    Test /api/me
    """
    def test_me_view_set_get_successful(self):
        """
        Successful /api/me GET

        :return:
        """
        # Create data
        user = account_models.User.objects.create_user(email='test@test.com', social_name='aeon', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me')
        result = request.data['result']

        self.assertEquals(result['email'], user.email)
        self.assertEquals(result['social_name'], user.social_name)
        self.assertEquals(result['username'], user.username)
