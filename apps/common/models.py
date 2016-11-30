from django.db import models
import datetime


class EditMixin(models.Model):
    """
    Abstract class for use in models

    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def get_uploaded_file_path(instance, filename):
    """
    Function that determines file path for specified file

    :param instance: instance of db object for which file is being saved
    :param filename: name of file
    :return: path to file
    """
    # If image has user, use username.{extension}
    # Else use name of file
    filename = '{}.{}'.format(instance.user.username, filename.split('.')[1]) if instance.user else filename

    # Date stamp
    # 2016-11-30_13:59:57
    current_time = str(str(datetime.datetime.now()).split('.')[0]).split('.')[0].replace(' ', '_')

    # 2016-11-30_13:59:57_{filename|username}.{ext}
    return '{}_{}'.format(current_time, filename.replace(' ', '_'))
