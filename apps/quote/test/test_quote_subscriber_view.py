from apps.quote.models import QuoteSubscriber
from rest_framework.test import APIClient
from django.test import TestCase


class TestQuoteSubscriberViewPOST(TestCase):
    """
    Test case to validate functionality of QuoteView
    """

    def tearDown(self):
        """Method to remove extraneous test data after each test"""
        QuoteSubscriber.objects.all().delete()

    def test_quote_subscriber_view_post_successful(self):
        """
        Unit test to verify successful retrieval of quotes
        """

        response = APIClient().post("/api/aov-web/quote-subscribers", data={"email": "test@test.com"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("email", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("modified_at", response.data)
