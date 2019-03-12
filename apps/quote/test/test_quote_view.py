from apps.quote.models import Quote
from rest_framework.test import APIClient
from django.test import TestCase
from django.utils import timezone


class TestQuoteViewGET(TestCase):
    """
    Test case to validate functionality of QuoteView
    """

    def setUp(self):
        """Method to set up test data"""
        # Create a new quote
        Quote.objects.create(
            quote="Great minds discuss ideas; average minds discuss events; small minds discuss people.",
            author="Eleanor Roosevelt", display_date=timezone.now().date())

    def tearDown(self):
        """Method to remove extraneous test data after each test"""
        Quote.objects.all().delete()

    def test_quote_view_get_successful(self):
        """Unit test to verify successful retrieval of quotes"""
        response = APIClient().get("/api/aov-web/quotes", format="json")
        results = response.data["results"][0]

        self.assertIn("quote", results)
        self.assertIn("display_date", results)
        self.assertIn("author", results)

    def test_quote_view_get_no_quote(self):
        """Unit test to verify an empty QuerySet if no quote for the day"""
        Quote.objects.all().delete()
        response = APIClient().get("/api/aov-web/quotes", format="json")
        results = response.data["results"]

        self.assertEqual(len(results), 0)
