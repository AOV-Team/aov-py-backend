from apps.account.models import User
from apps.common.test import helpers as test_helpers
from apps.discover.models import StatePhoto
from apps.photo.models import Photo, PhotoClassification
from apps.photo.photo import Photo as photo_Photo
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
import datetime


@override_settings(REMOTE_IMAGE_STORAGE=False)
class TestPhotoViewSetGET(TestCase):
    """
    Test GET api/photos
    """

    def setUp(self):
        """
            Method to create re-usable data for unit tests

        :return: None
        """
        user = User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1',
                                                       location="Boise", social_name="@theaov")
        category = PhotoClassification.objects.create_or_update(name='Night', classification_type='category')

        for number in range(1, 15):
            photo = Photo(coordinates=Point(-116, 43),
                           image=photo_Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')).compress(),
                           user=user)
            photo.save()
            photo.category.add(category)
            photo.votes = number
            photo.photo_feed.add(1)
            photo.save()
            
            # Create the StatePhoto entry to link State to Photo
            StatePhoto.objects.create(photo=photo, state_id=1)

    def tearDown(self):
        """
            Removes unnecessary test data after each unit test

        :return: None
        """

        User.objects.all().delete()
        Photo.objects.all().delete()
        StatePhoto.objects.all().delete()
        test_helpers.clear_directory('backend/media/', '*.jpg')

    def test_state_photo_view(self):
        """
        Test that retrieving photos for a state works, as well as pagination limits

        :return: None
        """
        client = APIClient()

        start_time = datetime.datetime.now()
        response = client.get("/api/aov-web/discover/states/1/photos")
        end_time = datetime.datetime.now()
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data["results"]), 12)
        self.assertLessEqual((end_time - start_time).total_seconds() * 1000.0, 200)
