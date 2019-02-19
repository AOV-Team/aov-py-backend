from apps.podcast import models as podcast_models
from django.test import override_settings, TestCase
from rest_framework.test import APIClient
from unittest import skip


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
                "location": "Boise"
            }

            request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 200)

    def test_new_request_with_image_jpeg(self):
        """
        Unit test to verify uploading a .jpeg works just like a .jpg

        :return: None
        """
        # Get data from endpoint
        client = APIClient()

        with open("apps/common/test/data/photos/jpeg.jpeg", "rb") as image:
            payload = {
                "image": image,
                "email": "user@test.com",
                "full_name": "testUsername",
                "location": "Boise"
            }

            request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 200)

    @override_settings(REMOTE_AUDIO_STORAGE=False)
    def test_new_request_with_audio_large_file(self):
        """
        Test case to make sure a new person can submit a request with an audio soundbite.

        :return: None
        """
        # Get data from endpoint
        client = APIClient()

        with open("apps/common/test/data/audio/allredct_gold_podcast_2.wav", "rb") as audio:
            payload = {
                "audio_sample": audio,
                "email": "user@test.com",
                "full_name": "testUsername",
                "location": "Boise",

            }

            request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 200)
        get_featured = podcast_models.GetFeaturedRequest.objects.get(requester_fk__email=payload["email"])
        self.assertIsNotNone(get_featured.audio)

    @skip("Uses 91 MB file. Expensive operation, don't run unless testing bandwidth")
    def test_new_request_with_audio_remote_large_file(self):
        """
        Test case to make sure a new person can submit a request with an audio soundbite.

        Audio is saved to S3

        :return: None
        """
        # Get data from endpoint
        client = APIClient()

        with open("apps/common/test/data/audio/allredct_gold_podcast_2.wav", "rb") as audio:
            payload = {
                "audio_sample": audio,
                "email": "user@test.com",
                "full_name": "testUsername",
                "location": "Boise",

            }

            request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 200)
        get_featured = podcast_models.GetFeaturedRequest.objects.get(requester_fk__email=payload["email"])
        self.assertIsNotNone(get_featured.audio)

    @override_settings(REMOTE_AUDIO_STORAGE=False)
    def test_new_request_with_audio_small_file(self):
        """
        Test case to make sure a new person can submit a request with an audio soundbite.

        :return: None
        """
        # Get data from endpoint
        client = APIClient()

        with open("apps/common/test/data/audio/musicbox.wav", "rb") as audio:
            payload = {
                "audio_sample": audio,
                "email": "user@test.com",
                "full_name": "testUsername",
                "location": "Boise",

            }

            request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 200)
        get_featured = podcast_models.GetFeaturedRequest.objects.get(requester_fk__email=payload["email"])
        self.assertIsNotNone(get_featured.audio)

    def test_new_request_with_audio_remote_small_file(self):
        """
        Test case to make sure a new person can submit a request with an audio soundbite.

        Audio is saved to S3

        :return: None
        """
        # Get data from endpoint
        client = APIClient()

        with open("apps/common/test/data/audio/musicbox.wav", "rb") as audio:
            payload = {
                "audio_sample": audio,
                "email": "user@test.com",
                "full_name": "testUsername",
                "location": "Boise",

            }

            request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 200)
        get_featured = podcast_models.GetFeaturedRequest.objects.get(requester_fk__email=payload["email"])
        self.assertIsNotNone(get_featured.audio)

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

    def test_new_request_with_story(self):
        """
        Unit test to verify an optional story can be submitted with the request, and we'll store it

        :return: None
        """
        # Get data from endpoint
        client = APIClient()

        payload = {
            "email": "user@test.com",
            "full_name": "testUsername",
            "location": "Boise",
            "story": "lorem ipsum blah blah blah"
        }

        request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 200)

    def test_new_request_with_camera(self):
        """
        Unit test to verify that the handling of the camera submissions works properly

        :return: None
        """
        client = APIClient()

        payload = {
            "email": "user@test.com",
            "full_name": "testUsername",
            "location": "Boise",
            "camera": ["Sony A7III", "Canon DSLR"]
        }

        request = client.post("/api/podcast/get_featured", data=payload, format="multipart")

        self.assertEqual(request.status_code, 200)
        self.assertEqual(podcast_models.Camera.objects.count(), 2)
