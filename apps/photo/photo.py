from django.core.files.images import ImageFile


class PhotoFile(ImageFile):
    def __init__(self, file_object):
        """
        Constructor

        :param file_object: object created using Python's open()
        :return: None
        """
        super(PhotoFile, self).__init__(file_object)
        self.obj = file_object
