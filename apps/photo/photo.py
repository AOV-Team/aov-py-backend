from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage as storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image as PillowImage


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
        super(Photo, self).__init__(file_object)
        self.obj = file_object
        self.pillow_image = PillowImage.open(file_object)

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
            img_ratio = self.pillow_image.size[0] / float(self.pillow_image.size[1])
            new_height = int(max_width / img_ratio)
            self.pillow_image = self.pillow_image.resize((max_width, new_height), PillowImage.ANTIALIAS)

        return self.pillow_image

    def save(self, filename, quality=100):
        """
        Save an image. Saves locally to media or remotely

        :param filename: name to give to image file
        :param quality: image quality
        :return: None
        """
        if settings.REMOTE_IMAGE_STORAGE:
            mem_img = BytesIO()
            self.pillow_image.save(fp=mem_img, format='JPEG', quality=quality)
            content = ContentFile(mem_img.getvalue())
            storage.save(filename, content)
        else:
            self.pillow_image.save('{}/{}'.format(settings.MEDIA_ROOT, filename), format='JPEG', quality=quality)
