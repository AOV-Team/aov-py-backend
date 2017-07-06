from apps.account import models as account_models
from django.test import override_settings, TestCase
from rest_framework.test import APIClient


@override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
class TestMarketplaceUserViewSetPOST(TestCase):
    """
    Test /api/marketplace/users POST (user creation)
    """

    def test_marketplace_user_view_set_post_successful(self):
        """
        Test that we can create a new user with an is_active value of false

        :return: None
        """
        # Create the payload for the user
        payload = {
            'email': 'test@test.com',
            'password': 'pass',
            'username': 'aov1'
        }

        c = APIClient()

        response = c.post('/api/marketplace/users', payload, format='json')

        self.assertEquals(response.status_code, 201)

        # Retrieve the user to check the is_active field
        user = account_models.User.objects.get(email=payload['email'])

        self.assertFalse(user.is_active)
