from apps.account import authenticate
from apps.account import models as account_models
from django.test import override_settings, TestCase
from rest_framework.test import APIClient
from unittest import skip


@skip("Urls turned off. Remove if featured turned back on.")
@override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
class TestMarketplaceActivationViewSetPOST(TestCase):
    """
    Test /api/marketplace/users/activate POST (user activation)
    """

    def test_marketplace_activation_view_set_post_successful(self):
        """
        Test that we can set the is_active of a new user to True using an activation code

        :return: None
        """
        # Create the payload for the user
        user_data = {
            'email': 'test@test.com',
            'password': 'pass',
            'username': 'aov1',
            'is_active': False
        }

        user = account_models.User.objects.create_user(**user_data)

        # Generate an activation code
        code = authenticate.create_authentication_code(user)

        payload = {
            "code": code
        }
        c = APIClient()

        response = c.post('/api/marketplace/users/activate', payload, format='json')

        self.assertEquals(response.status_code, 200)

        # Retrieve the user to check the is_active field
        user = account_models.User.objects.get(id=user.id)

        self.assertTrue(user.is_active)

    def test_marketplace_activation_view_set_post_no_code(self):
        """
        Test that we can set the is_active of a new user to True using an activation code

        :return: None
        """
        # Create the payload for the user
        user_data = {
            'email': 'test@test.com',
            'password': 'pass',
            'username': 'aov1',
            'is_active': False
        }

        user = account_models.User.objects.create_user(**user_data)

        payload = {}
        c = APIClient()

        response = c.post('/api/marketplace/users/activate', payload, format='json')

        self.assertEquals(response.status_code, 400)

        # Retrieve the user to check the is_active field
        user = account_models.User.objects.get(id=user.id)

        self.assertFalse(user.is_active)
