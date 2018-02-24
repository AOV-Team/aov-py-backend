from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings
from rest_framework.test import APIClient


@override_settings(REMOTE_IMAGE_STORAGE=False,
                   DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class TestGalleryViewSetGET(TestCase):
    def setUp(self):
        """
            Set up for the test suite. To be ran in between each test

        :return: No return
        """

        user = account_models.User.objects.create_user(email='mrtest@artofvisuals.com', password='WhoAmI',
                                                       username='aov1')
        photo = photo_models.Photo(coordinates=Point(-116, 43),
                                   image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo.save()
        photo2 = photo_models.Photo(coordinates=Point(-116, 43),
                                   image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo_models.Gallery.objects.create_or_update(
            name="Test Gallery", user=user, photos=photo_models.Photo.objects.all())

    def tearDown(self):
        """
            Clean out the data from each test for a clean slate

        :return: No return
        """

        account_models.User.objects.all().delete()
        photo_models.Photo.objects.all().delete()

    def test_gallery_get_successful(self):
        """
            Unit test to validate that the GET request to the GalleryViewSet works appropriately

        :return: No return
        :author: gallen
        """
        user = account_models.User.objects.get(username="aov1")
        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/user/galleries')
        results = request.data['results']

        print(results)