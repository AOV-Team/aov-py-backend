from apps.account import models as account_models
from django.test import TestCase
from rest_framework.test import APIClient


class TestUsersViewSetPOST(TestCase):
    """
    Test /api/me POST (user creation)
    """
    def test_users_view_set_post_basic_successful(self):
        """
        Successful /api/me POST

        :return: None
        """
        # Create user
        client = APIClient()

        payload = {
            'email': 'mrtest@mypapaya.io',
            'password': 'WhoWantsToBeAMillionaire?',
            'username': 'aov_hov'
        }

        request = client.post('/api/users', data=payload, format='json')
        result = request.data['result']

        self.assertEquals(request.status_code, 201)
        self.assertIn('email', result)
        self.assertIn('username', result)

        user = account_models.User.objects.get(email='mrtest@mypapaya.io')
        self.assertFalse(user.is_superuser)