from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.db.models.fields.files import ImageFieldFile
from io import BufferedReader, BytesIO
from PIL import Image as PillowImage
from PIL import ImageFilter, ImageCms
from storages.backends.s3boto3 import S3Boto3Storage
import io
import tempfile
import os


class Photo(ImageFile):
    """
    Class to manipulate image data

    References
    https://docs.djangoproject.com/en/1.10/_modules/django/core/files/uploadedfile/#InMemoryUploadedFile
    http://stackoverflow.com/questions/36417049/how-to-convert-an-inmemoryuploadedfile-in-django-to-a-fomat-for-flickr-api
    http://stackoverflow.com/questions/24373341/django-image-resizing-and-convert-before-upload
    http://stackoverflow.com/questions/9166400/convert-rgba-png-to-rgb-with-pil
    http://stackoverflow.com/questions/3723220/how-do-you-convert-a-pil-image-to-a-django-file

    """
    def __init__(self, file_object):
        """
        Constructor

        :param file_object: object created using Python's open()
        :return: None
        """
        if (isinstance(file_object, BufferedReader)
                or isinstance(file_object, InMemoryUploadedFile)
                or isinstance(file_object, TemporaryUploadedFile)
                or isinstance(file_object, ImageFieldFile)):
            super(Photo, self).__init__(file_object)
            self.obj = file_object
            self.pillow_image = self.convert()
        else:
            raise TypeError('File object not instance of BufferedReader, '
                            'InMemoryUploadedFile, ImageFieldFile or TemporaryUploadedFile')

    @staticmethod
    def needs_converted(image):
        """
            Return whether or not the image contains an icc_profile for ProPhoto RGB (ROMM) or AdobeRGB (1998)

        :param image: Image instance
        :return: Boolean
        """
        icc_profile = image.info.get("icc_profile")
        icc_bytes = io.BytesIO(icc_profile)

        try:
            profile = ImageCms.ImageCmsProfile(icc_bytes)
            profile_name = ImageCms.getProfileName(profile)
            return 'Adobe RGB' in profile_name or 'Reference Output Medium' in profile_name

        # Exception handling to capture the "cannot open profile from string" exception in the case of no icc_profile
        except OSError:
            return False

    def convert(self):
        """
            Convert an image from ProPhoto RGB/AdobeRGB (1998) color space to sRGB

            References:
            https://stackoverflow.com/a/41524153/1597697

        :return: Image open with PIL.Image's open()
        """
        image = PillowImage.open(self.obj)

        if self.needs_converted(image):
            # If the image uses the AdobeRGB (1998) or ProPhoto RGB color space, it will be converted to sRGB
            icc = tempfile.mkstemp(suffix='.icc')[1]
            with open(icc, 'wb') as f:
                f.write(image.info.get('icc_profile'))
                icc_filename = f.name
            srgb = ImageCms.createProfile('sRGB')
            image = ImageCms.profileToProfile(image, icc, srgb)

            try:
                os.remove(icc_filename)
            except OSError:
                pass

        # If the image is neither of the above, then just return the original image
        return image

    def compress(self, quality=80, max_width=2048):
        """
        Resize and save image to memory.
        Shortcut for resize() and save() except that it returns image as in-memory bytes

        :param quality: image quality
        :param max_width: max image width
        :return: BytesIO
        """
        self.resize(max_width=max_width)

        mem_img = BytesIO()
        self.pillow_image.save(fp=mem_img, format='JPEG', icc_profile=self.pillow_image.info.get('icc_profile'),
                               quality=quality)
        content = ContentFile(mem_img.getvalue())

        return InMemoryUploadedFile(content, None, self.name, 'image/jpeg', content.tell, None)

    def resize(self, max_width=2048):
        """
        Resize an image

        :param max_width: max width. Image will be resized if larger than this
        :return: Resized or original image (PIL Image object)
        """
        # Resize if larger than max
        if self.pillow_image.size[0] > max_width:
            self.pillow_image =  WidthResize(max_width).process(self.pillow_image)

        return self.pillow_image

    def save(self, filename, custom_bucket=False, quality=95):
        """
        Save an image. Saves locally to media or remotely

        :param filename: name to give to image file
        :param custom_bucket: If using remote storage, storage will use this bucket instead of the one set in
        settings.py
        :param quality: image quality
        :return: None
        """
        # Determine filetype by extension
        ext = filename.split('.')[-1]
        if ext == 'jpg':
            format = "JPEG"
        elif ext == 'png':
            format = "PNG"
        else:
            raise TypeError("Files of extension type {} are not supported.".format(ext))

        if settings.REMOTE_IMAGE_STORAGE:
            mem_img = BytesIO()
            self.pillow_image.save(fp=mem_img, format=format, quality=quality,
                                   icc_profile=self.pillow_image.info.get('icc_profile'))
            content = ContentFile(mem_img.getvalue())

            if custom_bucket:
                storage = S3Boto3Storage(bucket=custom_bucket)
            else:
                storage = S3Boto3Storage()

            return storage.save(filename, content)
        else:
            full_filename = '{}/{}'.format(settings.MEDIA_ROOT, filename)
            self.pillow_image.save(full_filename, format='JPEG', quality=quality,
                                   icc_profile=self.pillow_image.info.get('icc_profile'))

            return full_filename


class WidthResize(object):
    """
    Resize an image by setting the width and then calculating the height needed to maintain proportions
    """
    def __init__(self, width, upscale=False):
        self.width = width
        self.upscale = upscale

    def process(self, img):
        """
        Resize an image

        :param img: instance of Image to resize
        :return: resized Image
        """
        # Resize if larger than max
        if img.size[0] > self.width or self.upscale:
            img_ratio = img.size[0] / float(img.size[1])
            new_height = int(self.width / img_ratio)
            img = img.resize((self.width, new_height), PillowImage.ANTIALIAS)

        return img


class BlurResize(WidthResize):
    """
    Blur and resize an image
    """
    def __init__(self, width=300, upscale=False):
        super(BlurResize, self).__init__(width, upscale)

    def process(self, img):
        img = super(BlurResize, self).process(img)
        return img.filter(ImageFilter.GaussianBlur(radius=5))
