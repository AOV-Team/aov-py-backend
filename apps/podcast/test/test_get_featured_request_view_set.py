from apps.podcast import models as podcast_models
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient


class TestGetFeaturedRequestViewSetPOST(TestCase):
    """
    Class to verify the functionality of the GetFeaturedRequestView

    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_new_request_with_image(self):
        """
        Test case to make sure a new person can submit a request

        :return: None
        """

        # Get data from endpoint
        client = APIClient()

        with open("apps/common/test/data/photos/avatar.png", "rb") as image:
            payload = {
                "image": image,
                "email": "user@test.com",
                "full_name": "testUsername",
                "location": "Boise",

            }

            request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 200)

    def test_new_request_no_image(self):
        """
        Unit test to verify posting a new request works with no image

        :return: None
        """
        # Get data from endpoint
        client = APIClient()

        payload = {
            "email": "user@test.com",
            "full_name": "testUsername",
            "location": "Boise"
        }

        request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 200)

    def test_new_request_missing_email(self):
        """
        Unit test to verify that making a requesting without the email fails
        """
        # Get data from endpoint
        client = APIClient()

        payload = {
            "full_name": "testUsername",
            "location": "Boise"
        }

        request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 400)
        self.assertEqual(request.data["message"], "Missing required field email")

    def test_new_request_missing_full_name(self):
        """
        Unit test to verify that making a requesting without the full name fails
        """
        # Get data from endpoint
        client = APIClient()

        payload = {
            "email": "user@test.com",
            "location": "Boise"
        }

        request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 400)
        self.assertEqual(request.data["message"], "Missing required field full_name")

    def test_new_request_missing_location(self):
        """
        Unit test to verify that making a requesting without the location fails
        """
        # Get data from endpoint
        client = APIClient()

        payload = {
            "email": "user@test.com",
            "full_name": "testUsername"
        }

        request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 400)
        self.assertEqual(request.data["message"], "Missing required field location")
