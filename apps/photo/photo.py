from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from io import BufferedReader, BytesIO
from PIL import Image as PillowImage
from PIL import ImageFilter
from storages.backends.s3boto3 import S3Boto3Storage


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
        if isinstance(file_object, BufferedReader) \
                or isinstance(file_object, InMemoryUploadedFile) \
                or isinstance(file_object, TemporaryUploadedFile):
            super(Photo, self).__init__(file_object)
            self.obj = file_object
            self.pillow_image = PillowImage.open(file_object)
        else:
            raise TypeError('File object not instance of BufferedReader, InMemoryUploadedFile or TemporaryUploadedFile')

    def compress(self, quality=80, max_width=2000):
        """
        Resize and save image to memory.
        Shortcut for resize() and save() except that it returns image as in-memory bytes

        :param quality: image quality
        :param max_width: max image width
        :return: BytesIO
        """
        self.resize(max_width=max_width)

        mem_img = BytesIO()
        self.pillow_image.save(fp=mem_img, format='JPEG', quality=quality)
        content = ContentFile(mem_img.getvalue())

        return InMemoryUploadedFile(content, None, self.name, 'image/jpeg', content.tell, None)

    def resize(self, max_width=2000):
        """
        Resize an image

        :param max_width: max width. Image will be resized if larger than this
        :return: Resized or original image (PIL Image object)
        """
        # Resize if larger than max
        if self.pillow_image.size[0] > max_width:
            return WidthResize(max_width).process(self.pillow_image)

        return self.pillow_image

    def save(self, filename, custom_bucket=False, quality=100):
        """
        Save an image. Saves locally to media or remotely

        :param filename: name to give to image file
        :param custom_bucket: If using remote storage, storage will use this bucket instead of the one set in
        settings.py
        :param quality: image quality
        :return: None
        """
        if settings.REMOTE_IMAGE_STORAGE:
            mem_img = BytesIO()
            self.pillow_image.save(fp=mem_img, format='JPEG', quality=quality)
            content = ContentFile(mem_img.getvalue())

            if custom_bucket:
                storage = S3Boto3Storage(bucket=custom_bucket)
            else:
                storage = S3Boto3Storage()

            return storage.save(filename, content)
        else:
            full_filename = '{}/{}'.format(settings.MEDIA_ROOT, filename)
            self.pillow_image.save(full_filename, format='JPEG', quality=quality)

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
