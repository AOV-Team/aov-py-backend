from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings
from rest_framework.test import APIClient


@override_settings(REMOTE_IMAGE_STORAGE=False,
                   DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class TestUserStarredPhotosViewSetGET(TestCase):
    def setUp(self):
        """
            Set up for the test suite. To be ran in between each test

        :return: No return
        """

        user = account_models.User.objects.create_user(
            email='mrtest@artofvisuals.com', password='WhoAmI', username='aov2')
        photo = photo_models.Photo(coordinates=Point(-116, 43),
                                   image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                                   user=user)
        photo.save()
        photo2 = photo_models.Photo(coordinates=Point(-116, 43),
                                    image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                    user=user)
        photo2.save()
        account_models.UserInterest.objects.create(content_object=photo, user=user, interest_type='star')
        account_models.UserInterest.objects.create(content_object=photo2, user=user, interest_type='star')

    def tearDown(self):
        """
            Clean out the data from each test for a clean slate

        :return: No return
        """

        account_models.User.objects.all().delete()
        account_models.UserInterest.objects.all().delete()
        photo_models.Photo.objects.all().delete()

    def test_user_starred_photos_view_set_get_successful(self):
        """
            Unit test to verify retrieval of starred photos for a user works correctly

        :return: No return
        """
        user = account_models.User.objects.get(username="aov2")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)
        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/starred/photos')
        results = request.data['results']


        self.assertIn('next', request.data)
        self.assertEquals(len(results), 2)
        self.assertEquals(results[1]['latitude'], 43.0)
        self.assertEquals(results[1]['longitude'], -116.0)
        self.assertIsNotNone(results[0]['image_blurred'])
        self.assertIn('image_medium', results[0])
        self.assertIn('image_small', results[0])
        self.assertIn('image_small_2', results[0])
        self.assertIn('image_tiny_246', results[0])
        self.assertIn('image_tiny_272', results[0])
