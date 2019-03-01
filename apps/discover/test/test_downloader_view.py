import datetime
import random
from apps.discover import models as discover_models
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from django.core.files import File

@override_settings(REMOTE_AUDIO_STORAGE=False, REMOTE_IMAGE_STORAGE=False)
class DownloaderViewTestPOST(TestCase):
    """
    Class to test the creation of new Downloader objects
    """

    def setUp(self):
        # Create a sponsor to be used
        image_path = "apps/common/test/data/photos/avatar.png"
        pdf_path = "apps/common/test/data/files/small.pdf"
        with open(image_path, "rb") as image, open(pdf_path, "rb") as pdf:
            sponsor = discover_models.Sponsor.objects.create(name="Sponsor Alpha", social_handle="@SponsorAlpha",
                                                             website="https://www.sponsor-alpha.com",
                                                             profile_image=File(image, "test_image.png"),
                                                             downloadable_file=File(pdf, "test_pdf.pdf"))

        # Link the sponsor to a state
        discover_models.StateSponsor.objects.create(state=discover_models.State.objects.get(id=random.randint(1, 50)),
                                                    sponsor=sponsor, sponsorship_start=timezone.now(),
                                                    sponsorship_end=timezone.now() + datetime.timedelta(days=30))

    def tearDown(self):
        discover_models.Downloader.objects.all().delete()
        discover_models.StateSponsor.objects.all().delete()

    def test_downloader_view_new_downloader(self):
        """
        Test that a perfect scenario works as expected

        :return: None
        """

        c = APIClient()

        state_sponsor_id = discover_models.StateSponsor.objects.first().id
        downloader_data = {
            "name": "Prince McClinton",
            "email": "test@test.com",
            "location": "Boise",
            "state_sponsor": state_sponsor_id
        }

        http_response = c.post("/api/aov-web/discover/downloaders", data=downloader_data)

        self.assertEqual(http_response.status_code, 201)
        self.assertTrue("downloadable_file" in http_response.data)
