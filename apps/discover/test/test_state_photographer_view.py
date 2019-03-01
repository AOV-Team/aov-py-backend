from datetime import timedelta
from apps.discover import models as discover_models
from apps.photo.photo import Photo
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

@override_settings(REMOTE_IMAGE_STORAGE=False)
class TestStatePhotographerViewGET(TestCase):
    """
    Class to test the StatePhotographerView endpoint.
    """

    def setUp(self):
        """
        Method to configure the data

        :return: None
        """
        with open("apps/common/test/data/photos/avatar.png", "rb") as image:
            image = Photo(image).compress()
            name = "John Doe"
            social_handle = "@JDoe"

            photographer = discover_models.Photographer.objects.create(profile_image=image, name=name,
                                                                       social_handle=social_handle)
            discover_models.StatePhotographer.objects.create(state_id=1, photographer=photographer,
                                                             feature_start=timezone.now(),
                                                             feature_end=timezone.now() + timedelta(days=1))

    def tearDown(self):
        """
        Remove used test data

        :return: None
        """
        discover_models.Photographer.objects.all().delete()
        discover_models.StatePhotographer.objects.all().delete()

    def test_state_photographer_view_featured(self):
        """
        Unit test to verify if the photographer is the featured photographer, they are returned

        :return: None
        """

        client = APIClient()
        response = client.get("/api/aov-web/discover/states/1/photographers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_state_photographer_view_not_featured(self):
        """
        Unit test to verify that Photographers whose feature window has ended does not return in the response

        :return: None
        """
        # Retrieve the StatePhotographer to change the feature period
        state_photographer = discover_models.StatePhotographer.objects.first()
        state_photographer.feature_start = timezone.now() + timedelta(days=20)
        state_photographer.feature_end = timezone.now() + timedelta(days=21)
        state_photographer.save()

        client = APIClient()
        response = client.get("/api/aov-web/discover/states/1/photographers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)
