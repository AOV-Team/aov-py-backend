from apps.photo.photo import PhotoFile
from django.test import TestCase


class TestPhotoFile(TestCase):
    def test_photo_file_read_successful(self):
        """
        Test that we can open an image file

        :return: None
        """
        photo = PhotoFile(open('apps/common/test/data/photos/photo1-min.jpg', 'rb'))

        self.assertIsNotNone(photo.name)
        self.assertEquals(photo.width, 750)
        self.assertEquals(photo.height, 749)
