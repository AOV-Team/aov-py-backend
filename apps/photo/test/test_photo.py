from apps.photo.photo import Photo
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import override_settings, TestCase
from os.path import getsize


class TestPhoto(TestCase):
    def test_photo_read_successful(self):
        """
        Test that we can open an image file

        :return: None
        """
        photo = Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb'))

        self.assertIsNotNone(photo.name)
        self.assertEquals(photo.width, 750)
        self.assertEquals(photo.height, 749)

    def test_photo_compress(self):
        """
        Test that we can get compressed image in in-memory bytes

        :return: None
        """
        file = 'apps/common/test/data/photos/photo1-min.jpg'

        photo = Photo(open(file, 'rb'))
        image = photo.compress()

        self.assertIsInstance(image, InMemoryUploadedFile)

    @override_settings(IMAGES_USE_REMOTE_STORAGE=False)
    def test_photo_save_compressed_local(self):
        """
        Test that we can save compressed images in media

        :return: None
        """
        file = 'apps/common/test/data/photos/photo1-min.jpg'
        saved = settings.MEDIA_ROOT + '/img.jpg'

        photo = Photo(open(file, 'rb'))
        photo.resize(max_width=2000)
        photo.save(saved, quality=80)

        self.assertLess(getsize(file), getsize(saved))
