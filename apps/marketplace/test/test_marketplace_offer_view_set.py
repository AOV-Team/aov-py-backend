from apps.account import authenticate
from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.marketplace import models as marketplace_models
from django.test import override_settings, TestCase
from rest_framework.test import APIClient


@override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
class TestMarketplaceOfferViewSetPOST(TestCase):
    """
        Test class for the POST method of the MarketplaceOfferViewSet
    """

    def test_marketplace_offer_view_set_post_successful(self):
        """
            Test of everything working correctly

        :return: No return value
        """

        # Create the user to be used in the test
        owner = account_models.User.objects.create_user(email="owner@testaov.com", password="Owner", username="owner")
        buyer = account_models.User.objects.create_user(email="buyer@testaov.com", password="Buyer", username="buyer")

        listing = marketplace_models.Listing.objects.create(owner=owner, category="C", brand="Nikon",
                                                            title="Lightly used camera for sale", price="299.99",
                                                            paypal_email="test@paypal.me")

        # Simulate auth
        token = test_helpers.get_token_for_user(buyer)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        data = {
            'owner': owner.id,
            'listing_id': listing.id,
            'amount': "250.00"
        }

        response = client.post('/api/marketplace/offers', data=data, format='json')

        self.assertEqual(response.status_code, 201)

        self.assertIsInstance(response.data, dict)
        self.assertEqual(response.data["listing"]["id"], listing.id)
        self.assertEqual(response.data["owner"]["id"], owner.id)
        self.assertEqual(response.data["buyer"]["id"], buyer.id)
        self.assertEqual(response.data["offer_value"], data["amount"])
        self.assertEqual(response.data["status"], "O")
