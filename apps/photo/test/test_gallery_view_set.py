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

        account_models.User.objects.create_user(email='mrtest@artofvisuals.com', password='WhoAmI', username='aov2')
        target_user = account_models.User.objects.create_user(email='mrstest@artofvisuals.com', password='WhoAmI',
                                                              username='aov1')
        photo = photo_models.Photo(coordinates=Point(-116, 43),
                                   image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                                   user=target_user)
        photo.save()
        photo2 = photo_models.Photo(coordinates=Point(-116, 43),
                                    image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                    user=target_user)
        photo2.save()
        photo_models.Gallery.objects.create_or_update(
            name="Test Gallery", user=target_user, photos=photo_models.Photo.objects.all())

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
        user = account_models.User.objects.get(username="aov2")
        # Simulate auth
        token = test_helpers.get_token_for_user(user)
        target_user = account_models.User.objects.get(username="aov1")

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/galleries'.format(target_user.id))
        results = request.data['results']

        self.assertEqual(request.status_code, 200)
        self.assertEqual(results[0]["photo_count"], 2)

    def test_gallery_get_me_successful(self):
        """
            Unit test to verify that private Galleries can be retrieved by the authenticated user

        :return: No return
        """

        user = account_models.User.objects.get(username="aov2")
        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Set the Gallery to private
        gallery = photo_models.Gallery.objects.first()
        gallery.public = False
        gallery.user = user
        gallery.save()

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/galleries')
        results = request.data['results']

        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["photo_count"], 2)
