from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.contrib.gis.geos import Point
from django.test import override_settings, TestCase
from rest_framework.test import APIClient
import datetime
import random


@override_settings(REMOTE_IMAGE_STORAGE=False)
class TestPhotoSingleMediaView(TestCase):
    """
    Test GET api/photos
    """

    def setUp(self):
        """
            Method to create re-usable data for unit tests

        :return: None
        """
        user = account_models.User.objects.create_user(email="mrtest@mypapaya.io", password="WhoAmI", username="aov1",
                                                       location="Boise", social_name="@theaov")
        category = photo_models.PhotoClassification.objects.create_or_update(name="Night",
                                                                             classification_type="category")

        # Create some gear
        gear_1 = account_models.Gear.objects.create_or_update(item_make="Canon", item_model="EOS 5D Mark II")
        gear_2 = account_models.Gear.objects.create_or_update(item_make="Sony", item_model="a99 II")

        photo1 = photo_models.Photo(coordinates=Point(-116, 43),
                                    image=Photo(open("apps/common/test/data/photos/photo1-min.jpg", "rb")),
                                    user=user)
        photo1.save()
        photo1.gear.add(gear_1, gear_2)
        photo1.category.add(category)
        photo1.votes = random.randint(0, 100)
        photo1.photo_feed.add(1)
        photo1.save()

    def tearDown(self):
        """
            Removes unnecessary test data after each unit test

        :return: None
        """

        account_models.User.objects.all().delete()
        photo_models.Photo.objects.all().delete()
        test_helpers.clear_directory("backend/media/", "*.jpg")

    def test_photo_single_media_view_all_renders(self):
        """
        Test that we can get a Photo with all standard renders, in under 200ms
    
        :return: None
        """
        # Get data from endpoint
        client = APIClient()

        start_time = datetime.datetime.now()
        request = client.get("/api/photos/{}/media".format(photo_models.Photo.objects.first().id))
        end_time = datetime.datetime.now()
        results = request.data["results"]

        self.assertIn("next", request.data)
        self.assertEquals(len(results), 1)
        self.assertTrue("gear" not in results[0])
        self.assertTrue("latitude" not in results[0])
        self.assertTrue("longitude" not in results[0])
        self.assertTrue("votes" not in results[0])
        self.assertTrue("votes_behind" not in results[0])
        self.assertTrue("user" not in results[0])
        self.assertTrue("user_details" not in results[0])
        self.assertTrue("category" not in results[0])
        self.assertTrue("comments" not in results[0])
        self.assertTrue("image" in results[0])
        self.assertTrue("image_blurred" in results[0])
        self.assertTrue("image_medium" in results[0])
        self.assertTrue("image_small" in results[0])
        self.assertTrue("image_small_2" in results[0])
        self.assertTrue("image_tiny_246" in results[0])
        self.assertTrue("image_tiny_272" in results[0])
        self.assertLessEqual((end_time-start_time).total_seconds() * 1000.0, 200)

    def test_photo_single_media_view_custom_render(self):
        """
        Test that we can get a custom sized render for a single Photo in under 200 ms

        :return: None
        """

        # Get data from endpoint
        client = APIClient()

        start_time = datetime.datetime.now()
        request = client.get(
            "/api/photos/{}/media?height=1920&width=1080".format(photo_models.Photo.objects.first().id))
        end_time = datetime.datetime.now()
        results = request.data["results"]

        self.assertIn("next", request.data)
        self.assertEquals(len(results), 1)
        self.assertTrue("image" in results[0])
        self.assertTrue("gear" not in results[0])
        self.assertTrue("latitude" not in results[0])
        self.assertTrue("longitude" not in results[0])
        self.assertTrue("votes" not in results[0])
        self.assertTrue("votes_behind" not in results[0])
        self.assertTrue("user" not in results[0])
        self.assertTrue("user_details" not in results[0])
        self.assertTrue("category" not in results[0])
        self.assertTrue("comments" not in results[0])
        self.assertTrue("image_blurred" not in results[0])
        self.assertTrue("image_medium" not in results[0])
        self.assertTrue("image_small" not in results[0])
        self.assertTrue("image_small_2" not in results[0])
        self.assertTrue("image_tiny_246" not in results[0])
        self.assertTrue("image_tiny_272" not in results[0])
        self.assertLessEqual((end_time - start_time).total_seconds() * 1000.0, 200)
