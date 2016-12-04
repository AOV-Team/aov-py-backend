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


def build_file_name(date_stamp, filename):
    """
    Builds name of image file
    e.g. 2016-11-30_135957_{filename[.ext]}

    :param date_stamp: date/date time stamp to prepend to image name
    :param filename: name of image
    :return: String with formatted file name
    """
    return '{}_{}'.format(date_stamp, filename.replace(' ', '_'))


def get_date_stamp_str():
    """
    Date stamp
    e.g. 2016-11-30_135957

    :return: Date stamp str
    """
    return str(str(datetime.datetime.now()).split('.')[0]).replace(':', '').replace(' ', '_')


def get_uploaded_file_path(instance, filename):
    """
    Function that determines file path for specified file

    :param instance: instance of db object for which file is being saved
    :param filename: name of file
    :return: path to file
    """
    # If image has user, use username.{extension}
    # Else use name of file
    try:
        filename = 'u{}.{}'\
            .format(instance.user.id, filename.split('.')[-1]) if instance.user else filename
    except AttributeError:
        # Instance is of type User
        filename = 'AVATAR_{}.{}'.format(instance.email, filename.split('.')[-1])

    # Date stamp
    current_time = get_date_stamp_str()

    # 2016-11-30_135957_{filename|username}.{ext}
    return build_file_name(current_time, filename)

