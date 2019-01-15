from django.contrib.gis.db import models as geo_models
from django.db import models
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


def get_uploaded_file_path(instance, filename):
    """
    Function that determines file path for specified file

    :param instance: instance of db object for which file is being saved
    :param filename: name of file
    :return: path to file
    """
    # If image has user, use username.{extension}
    # Else use name of file

    if hasattr(instance, "user"):
        filename = 'u{}.{}'.format(instance.user.id, filename.split('.')[-1])

    elif hasattr(instance, "requester_fk"):
        filename = 'AVATAR_{}.{}'.format(instance.requester_fk.email, filename.split('.')[-1])

    elif hasattr(instance, "gender") and instance.__str__() == "User":
        # Instance is of type User
        filename = 'AVATAR_{}.{}'.format(instance.email, filename.split('.')[-1])


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
