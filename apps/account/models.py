from apps.common import models as common_models
from apps.common.exceptions import OverLimitException
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class GearManager(models.Manager):
    def create_or_update(self, **kwargs):
        """
        Creates new entry or updates if Gear entry already exists

        :param kwargs:
        :return: instance of Gear
        """
        new_gear = Gear(**kwargs)
        existing = Gear.objects.filter(make=new_gear.make, model=new_gear.model).first()

        if existing:
            new_gear.pk = existing.pk
            new_gear.id = existing.id

        new_gear.save()
        return new_gear


class Gear(models.Model):
    link = models.URLField(blank=True, null=True)
    make = models.TextField(max_length=128)
    model = models.TextField(max_length=128)
    public = models.BooleanField(default=True)
    reviewed = models.BooleanField(default=False)  # Set to true if added/approved by AOV

    objects = GearManager()

    @property
    def name(self):
        return '{} {}'.format(self.make, self.model)

    def __str__(self):
        """
        String representation of gear

        :return: String
        """

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ('make', 'model',)
        verbose_name_plural = 'gear'


class UserCustomManager(BaseUserManager):
    def _create_user(self, email, password, username, is_superuser, **extra_fields):
        now = timezone.now()

        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_admin=is_superuser,
                          is_superuser=is_superuser,
                          last_login=now,
                          username=username, **extra_fields)

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        return self._create_user(email, password, username, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        # By default username is email
        return self._create_user(email, password, email, True, **extra_fields)


class User(AbstractBaseUser, common_models.EditMixin, PermissionsMixin):
    gear = models.ManyToManyField(Gear, blank=True)

    age = models.PositiveSmallIntegerField(blank=True, null=True)
    avatar = models.ImageField(upload_to=common_models.get_uploaded_file_path, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=64, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False, verbose_name='staff account')
    last_name = models.CharField(max_length=64, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    social_name = models.CharField(max_length=64, blank=True,
                                   null=True)  # third party social platforms such as Instagram
    username = models.CharField(max_length=255, unique=True)

    USERNAME_FIELD = 'email'
    objects = UserCustomManager()

    class Meta:
        verbose_name_plural = "Users"

    def get_short_name(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return '{},\t{},\tID{}'.format(self.username, self.email, self.id)

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')


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

    objects = ProfileManager()

    def __str__(self):
        return '{}:\tID{}'.format(self.user.username, self.id)

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')


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
    interest_type = models.CharField(max_length=10, choices=INTEREST_TYPE_CHOICES)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return '{} {}: {}'.format(self.interest_type, self.content_object, self.object_id)

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
