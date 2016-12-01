from django.core.files.images import ImageFile
from PIL import Image


class Photo(ImageFile):
    def __init__(self, file_object):
        """
        Constructor

        :param file_object: object created using Python's open()
        :return: None
        """
        super(Photo, self).__init__(file_object)
        self.obj = file_object
        self.img = Image.open(file_object)

    def resize(self, max_width=2000):
        """
        Resize an image

        :param max_width: max width. Image will be resized if larger than this
        :return: Resized or original image (PIL Image object)
        """
        # Resize if larger than max
        if self.img.size[0] > max_width:
            img_ratio = self.img.size[0] / float(self.img.size[1])
            new_height = int(max_width / img_ratio)
            self.img = self.img.resize((max_width, new_height), Image.ANTIALIAS)

        return self.img

    def save(self, filename, quality=100):
        """
        Save an image.

        :param filename: name to give to image file
        :param quality: image quality
        :return: None
        """
        self.img.save(filename, format='JPEG', quality=quality)
