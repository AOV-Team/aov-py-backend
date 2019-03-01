from datetime import timedelta
from apps.discover import models as discover_models
from django.core.files import File
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
        image_path = "apps/common/test/data/photos/avatar.png"
        pdf_path = "apps/common/test/data/files/small.pdf"
        with open(image_path, "rb") as image, open(pdf_path, "rb") as pdf:
            sponsor = discover_models.Sponsor.objects.create(name="Sponsor Alpha", social_handle="@SponsorAlpha",
                                                             website="https://www.sponsor-alpha.com",
                                                             profile_image=File(image, "test_image.png"),
                                                             downloadable_file=File(pdf, "test_pdf.pdf"))
            discover_models.StateSponsor.objects.create(state_id=1, sponsor=sponsor,
                                                        sponsorship_start=timezone.now(),
                                                        sponsorship_end=timezone.now() + timedelta(days=1))

    def tearDown(self):
        """
        Remove used test data

        :return: None
        """
        discover_models.Sponsor.objects.all().delete()
        discover_models.StateSponsor.objects.all().delete()

    def test_state_sponsor_view_active(self):
        """
        Unit test to verify if the sponsor is the current sponsor, they are returned

        :return: None
        """

        client = APIClient()
        response = client.get("/api/aov-web/discover/states/1/sponsors")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_state_sponsor_view_not_active(self):
        """
        Unit test to verify that Photographers whose feature window has ended does not return in the response

        :return: None
        """
        # Retrieve the StatePhotographer to change the feature period
        state_sponsor = discover_models.StateSponsor.objects.first()
        state_sponsor.sponsorship_start = timezone.now() + timedelta(days=20)
        state_sponsor.sponsorship_end = timezone.now() + timedelta(days=21)
        state_sponsor.save()

        client = APIClient()
        response = client.get("/api/aov-web/discover/states/1/sponsors")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)
