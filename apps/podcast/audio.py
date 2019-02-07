from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from storages.backends.s3boto3 import S3Boto3Storage
import io


class Audio(File):
    """
    Class to handle Audio files

    """

    def __init__(self, file_object):
        """
        Constructor

        :param file_object: object created using Python's open()
        :return: None
        """
        if (isinstance(file_object, io.BufferedReader)
            or isinstance(file_object, InMemoryUploadedFile)
            or isinstance(file_object, TemporaryUploadedFile)):

            super(Audio, self).__init__(file_object)
            self.obj = file_object
        else:
            raise TypeError('File object not instance of BufferedReader, '
                            'InMemoryUploadedFile or TemporaryUploadedFile')

    def save(self, filename, custom_bucket=False):
        """
        Save an audio file. Saves locally to media or remotely

        :param filename: name to give to the audio file
        :param custom_bucket: If using remote storage, storage will use this bucket instead of the one set in
        settings.py
        :return: either the remote_key
        """
        if settings.REMOTE_AUDIO_STORAGE:
            if custom_bucket:
                storage = S3Boto3Storage(bucket=custom_bucket)
            else:
                storage = S3Boto3Storage()

            return storage.save(filename, self.obj)
        else:
            full_filename = '{}/{}'.format(settings.MEDIA_ROOT, filename)

            return full_filename
