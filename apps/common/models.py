from django.contrib.gis.db import models as geo_models
from django.db import models
from os.path import splitext
import datetime
import random


class EditMixin(models.Model):
    """
    Abstract class for use in models

    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class GeoEditMixin(geo_models.Model):
    """
        Abstract class for use in models that inherit from geo_models version of Model, avoids MRO TypeError

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


def get_random_queryset_elements(queryset, number, yield_object=True):
    """
    Adapted from https://www.peterbe.com/plog/getting-random-rows-postgresql-django

    :param queryset: queryset to select elements from
    :param number: number of random elements to return
    :param yield_object: if True, returns model object, else it returns just the id
    :return:
    """
    assert number <= 10000, 'too large'
    max_pk = queryset.aggregate(models.Max('pk'))['pk__max']
    min_pk = queryset.aggregate(models.Min('pk'))['pk__min']
    ids = set()

    while len(ids) < number:
        next_pk = random.randint(min_pk, max_pk)

        while next_pk in ids:
            next_pk = random.randint(min_pk, max_pk)

        try:
            found = queryset.get(pk=next_pk)
            ids.add(found.pk)

            if yield_object:
                yield found
            else:
                yield found.pk
        except queryset.model.DoesNotExist:
            pass


def get_podcast_file_path(instance, filename):
    """
    Function that determines a filepath for audio files

    :param instance: Instance of a db object for which the file is being saved
    :param filename: Name of file
    :return: Path to the file
    """

    # It's a GetFeatured audio file
    if hasattr(instance, "reviewed"):
        filename = "GET_FEATURED_AUDIO.{}".format(filename.split('.')[-1])

    # It's a Podcast Episode
    elif hasattr(instance, "archived"):
        filename = "PODCAST_{}.{}".format(instance.title, filename.split('.')[-1])

    return build_file_name(get_date_stamp_str(), filename)


def get_uploaded_file_path(instance, filename):
    """
    Function that determines file path for specified file

    :param instance: instance of db object for which file is being saved
    :param filename: name of file
    :return: path to file
    """
    # If image has user, use username.{extension}
    # Else use name of file

    file_ext = filename.split('.')[-1]
    instance_class = instance.__str__()

    if hasattr(instance, "user") and instance.user:
        filename = 'u{}.{}'.format(instance.user.id, file_ext)

    elif hasattr(instance, "requester_fk"):
        filename = 'GET_FEATURED.{}'.format(file_ext)

    elif hasattr(instance, "gender") and instance_class == "User":
        # Instance is of type User
        filename = 'AVATAR_{}.{}'.format(instance.email, file_ext)

    elif instance_class == "State":
        filename = "STATE_ICON_{}.{}".format(instance.name, file_ext)

    elif instance_class == "Sponsor":
        # Check if it's the profile image or the downloadable file by checking the file extension
        if file_ext in ["jpg", "jpeg", "png"]:
            # This is the profile image
            filename = "SPONSOR_IMAGE_{}.{}".format(instance.name, file_ext)
        else:
            filename = "INFO_GUIDE_BY_{}.{}".format(instance.name, file_ext)

    elif instance_class == "Photographer":
        filename = "PHOTOGRAPHER_PROFILE.{}".format(file_ext)

    else:
        filename = "{}.{}".format(splitext(filename)[0], file_ext)

    # Date stamp
    current_time = get_date_stamp_str()

    # 2016-11-30_135957_{filename|username}.{ext}
    return build_file_name(current_time, filename)


def get_classification_background_file_path(instance, filename):
    """
        Function that determines file path for specified file

    :param instance: instance of db object for which file is being saved
    :param filename: name of file
    :return: path to file
    """
    new_filename = "{}_background.{}".format(instance.name.lower(), filename.split('.')[-1])

    filepath = "{}".format(new_filename.replace(' ', '_'))

    return filepath


def get_classification_icon_file_path(instance, filename):
    """
        Function that determines file path for specified file

    :param instance: instance of db object for which file is being saved
    :param filename: name of file
    :return: path to file
    """

    new_filename = "{}_icon.{}".format(instance.name.lower(), filename.split('.')[-1])

    filepath = "{}".format(new_filename.replace(' ', '_'))

    return filepath
