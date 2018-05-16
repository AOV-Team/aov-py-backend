from apps.photo.photo import Photo, BlurResize, WidthResize
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import override_settings, TestCase
from os.path import getsize
from PIL import Image, ImageCms
import io


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

    def test_photo_bad_type(self):
        """
        Test that we get TypeError if we don't supply a file

        :return: None
        """
        with self.assertRaises(TypeError):
            Photo('foo')

    def test_photo_compress(self):
        """
        Test that we can get compressed image in in-memory bytes

        :return: None
        """
        file = 'apps/common/test/data/photos/md-portrait.jpg'

        photo = Photo(open(file, 'rb'))
        image = photo.compress()

        pil_image = Image.open(image)

        self.assertIsInstance(image, InMemoryUploadedFile)
        self.assertEquals(pil_image.size[0], 2048)

    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_save_compressed_local(self):
        """
        Test that we can save compressed images in media

        :return: None
        """
        file = 'apps/common/test/data/photos/photo1-min.jpg'
        saved = 'img.jpg'

        photo = Photo(open(file, 'rb'))
        photo.resize(max_width=2000)
        photo.save(saved, quality=80)

        self.assertLess(getsize(file), getsize('{}/{}'.format(settings.MEDIA_ROOT, saved)))

    def test_photo_save_remote_custom_bucket(self):
        """
        Test that we can save to custom remote bucket

        :return: None
        """
        file = 'apps/common/test/data/photos/cover.jpg'

        photo = Photo(open(file, 'rb'))
        saved = photo.save('custom_bucket.jpg', custom_bucket='aovdev1', quality=80)

        self.assertIsNotNone(saved)


class TestBlurResize(TestCase):
    """
    Test that we can resize and blur an image
    """
    def test_blur_resize_successful(self):
        """
        Test that image is resized to 300px wide

        :return: None
        """
        f = 'apps/common/test/data/photos/4mb.jpg'
        img = Image.open(f)

        image = BlurResize()
        new_img = image.process(img)

        self.assertEquals(new_img.size[0], 300)
        self.assertEquals(new_img.size[1], 373)

    def test_blur_resize_upscale(self):
        """
        Test that we can blur + resize an image and that it upscales

        :return: None
        """
        f = 'apps/common/test/data/photos/photo1-min.jpg'
        img = Image.open(f)

        image = BlurResize(width=2048, upscale=True)
        new_img = image.process(img)

        self.assertEquals(new_img.size[0], 2048)
        self.assertEquals(new_img.size[1], 2045)


class TestWidthResize(TestCase):
    def test_width_resize_successful(self):
        """
        Test that we can resize an image

        :return: None
        """
        f = 'apps/common/test/data/photos/4mb.jpg'
        img = Image.open(f)

        image = WidthResize(width=1242)
        new_img = image.process(img)

        self.assertEquals(new_img.size[0], 1242)
        self.assertEquals(new_img.size[1], 1548)

    def test_width_resize_no_upscale(self):
        """
        Test that we can resize an image and that it does not upscales

        :return: None
        """
        f = 'apps/common/test/data/photos/photo1-min.jpg'
        img = Image.open(f)

        image = WidthResize(width=2048, upscale=False)
        new_img = image.process(img)

        self.assertEquals(new_img.size[0], 750)
        self.assertEquals(new_img.size[1], 749)

    def test_width_resize_upscale(self):
        """
        Test that we can resize an image and that it upscales

        :return: None
        """
        f = 'apps/common/test/data/photos/photo1-min.jpg'
        img = Image.open(f)

        image = WidthResize(width=2048, upscale=True)
        new_img = image.process(img)

        self.assertEquals(new_img.size[0], 2048)
        self.assertEquals(new_img.size[1], 2045)
