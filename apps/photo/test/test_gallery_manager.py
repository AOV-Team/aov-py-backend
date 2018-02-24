from apps.account import models as account_models
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings


@override_settings(REMOTE_IMAGE_STORAGE=False,
                   DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class TestGalleryManager(TestCase):
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

    def tearDown(self):
        """
            Clean out the data from each test for a clean slate

        :return: No return
        """

        account_models.User.objects.all().delete()
        photo_models.Photo.objects.all().delete()


    def test_gallery_successful(self):
        """
        Test that we can create a new Gallery

        :return: None
        """
        user = account_models.User.objects.filter(username="aov1").first()

        photo_models.Gallery.objects.create_or_update(user=user, photos=photo_models.Photo.objects.all(),
                                                      name="Personal")

        gallery = photo_models.Gallery.objects.filter(name="Personal")
        self.assertTrue(gallery.exists())

    def test_gallery_adding_with_different_photos(self):
        """
            Unit test to validate that if an attempt is made to create a gallery with the same name, but different
            photos, it adds the new photos to the existing gallery.

        :return: No return
        """

        user = account_models.User.objects.filter(username="aov1").first()

        photo_models.Gallery.objects.create_or_update(user=user, photos=photo_models.Photo.objects.all(),
                                                      name="Personal")

        gallery = photo_models.Gallery.objects.filter(name="Personal")
        self.assertTrue(gallery.exists())

        photo =photo_models.Photo(coordinates=Point(-116, 43),
                           image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo.save()

        photo_models.Gallery.objects.create_or_update(user=user, photos=photo_models.Photo.objects.all(),
                                                      name="Personal")

        gallery = photo_models.Gallery.objects.filter(name="Personal")
        self.assertEqual(gallery.values_list("photos", flat=True).count(), 2)
