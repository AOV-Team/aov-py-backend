from apps.common import models as common_models
from apps.common.exceptions import OverLimitException
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
import json


class UserCustomManager(BaseUserManager):
    def _create_user(self, email, password, username, is_superuser, **extra_fields):
        now = timezone.now()

        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_superuser=is_superuser,
                          last_login=now,
                          username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        return self._create_user(email, password, username, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        # By default username is email
        return self._create_user(email, password, email, True, **extra_fields)


class User(AbstractBaseUser, common_models.EditMixin, PermissionsMixin):
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    avatar = models.ImageField(upload_to=common_models.get_uploaded_file_path, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=64, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    social_name = models.CharField(max_length=64, blank=True,
                                   null=True)  # third party social platforms such as Instagram
    username = models.CharField(max_length=255, unique=True)

    USERNAME_FIELD = 'email'
    objects = UserCustomManager()

    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser

    def __str__(self):
        return '{},\t{},\tID{}'.format(self.username, self.email, self.id)


class Gear:
    """
    Class for managing a profile's gear
    """
    def __init__(self, profile, gear=None):
        """
        Format for gear
        [
            {
                name: ''
                link: ''
            }
        ]

        :param profile: instance of Profile
        :param gear: list of dictionaries containing gear info
        """
        self.gear = gear
        self.profile = profile

    @property
    def all(self):
        """
        Retrieve all gear

        :return: list
        """
        if not self.profile.gear:
            return list()
        else:
            return json.loads(self.profile.gear)

    def links_valid(self, new_data):
        """
        Check that links match existing links and that no new links have been added.
        Used by PATCH endpoint to ensure that links cannot be created via API

        :param new_data: The data to be saved that needs to be checked
        :return: boolean
        """
        old_data = self.all

        for i in new_data:
            if 'make' not in i or 'model' not in i:
                raise KeyError('Make and model required')

            # If there's a link in the new data, check it
            if 'link' in i:
                # Find matches of new data in old
                matches = list()

                for d in old_data:
                    if d['make'] == i['make'] and d['model'] == i['model']:
                        matches.append(d)

                # Make sure that link is the same of at least one of the links of the existing items
                link_matches = 0

                for m in matches:
                    if 'link' in m:
                        if m['link'] == i['link']:
                            link_matches += 1

                if link_matches == 0:
                    return False

        return True

    def save(self):
        """
        Saves gear to profile instance

        :return: Profile instance
        """
        if self.gear:
            # Cannot have more than 8 items
            if len(self.gear) > 8:
                raise OverLimitException('User cannot have more than 8 gear items')

            # Perform checks on data
            for i in self.gear:
                # Make and model are mandatory
                if 'make' not in i or 'model' not in i:
                    raise KeyError('Make and model required')

                # Only make, model, and link are allowed
                for key in i.keys():
                    if key == 'make' or key == 'model' or key == 'link':
                        pass
                    else:
                        raise ValueError('Invalid key {} found'.format(key))

            self.profile.gear = json.dumps(self.gear)
            self.profile.save()
        else:
            self.profile.gear = json.dumps(list())
            self.profile.save()

        return self.profile


class ProfileManager(models.Manager):
    def create_or_update(self, **kwargs):
        """
        Creates new entry or updates if Profile entry already exists

        :param kwargs:
        :return: instance of Profile
        """
        new_profile = Profile(**kwargs)
        existing = Profile.objects.filter(user=new_profile.user).first()

        if existing:
            new_profile.pk = existing.pk
            new_profile.id = existing.id

        new_profile.save()
        return new_profile


class Profile(models.Model):
    user = models.ForeignKey(User)
    bio = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to=common_models.get_uploaded_file_path, blank=True, null=True)
    gear = models.TextField(blank=True, null=True)

    objects = ProfileManager()

    def __str__(self):
        return '{}:\tID{}'.format(self.user.username, self.id)


class UserInterest(models.Model):
    """
    Model for user likes and photo stars

    References
    https://docs.djangoproject.com/en/1.10/ref/contrib/contenttypes/#generic-relations
    https://github.com/pinax/pinax-likes/blob/master/pinax/likes/models.py
    http://stackoverflow.com/questions/21212654/with-django-how-can-i-retrieve-if-the-user-likes-the-article-of-other-items
    https://makina-corpus.com/blog/metier/2015/how-to-improve-prefetch_related-performance-with-the-prefetch-object
    """
    INTEREST_TYPE_CHOICES = (
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('star', 'Star'),
    )

    user = models.ForeignKey(User)
    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    interest_type = models.CharField(max_length=10, choices=INTEREST_TYPE_CHOICES)

    def __str__(self):
        return '{} {}: {}'.format(self.interest_type, self.content_object, self.object_id)
