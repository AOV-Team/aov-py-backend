import datetime
import random
from apps.account.models import User
from apps.discover import models as discover_models
from django.core.files import File
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


class DownloaderModelAdminTest(TestCase):
    """
    Class to test the CSV download action for Downloader objects
    """

    def setUp(self):
        # Create the related objects which will allow us to create the Downloader object needed for the test
        with open("apps/common/test/data/files/small.pdf", "rb") as pdf:
            sponsor = discover_models.Sponsor.objects.create(name="State Sponsor", social_handle="@test-account",
                                                             website="https://www.test.com",
                                                             downloadable_file=File(pdf, "test_pdf.pdf"))
            state_sponsor = discover_models.StateSponsor.objects.create(
                sponsor=sponsor, sponsorship_start=timezone.now(),
                sponsorship_end=timezone.now() + datetime.timedelta(days=1),
                state=discover_models.State.objects.get(id=random.randint(1, 49)))

        self.downloader = discover_models.Downloader.objects.create(state_sponsor=state_sponsor, name="Me",
                                                                    email="downloader@test.com", location="New York")
        self.username = "test-user"
        self.password = "test-pass"
        self.user = User.objects.create_superuser(self.username,  self.password)

    def test_download_csv_action(self):
        """
        Test to verify that downloading a csv works properly from admin site

        :return: None
        """

        data = {
            "action": "download_csv",
            "_selected_action": [self.downloader.id, ]
        }
        change_url = reverse("admin:discover_downloader_changelist")
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()

        self.assertEqual(response.status_code, 200)
