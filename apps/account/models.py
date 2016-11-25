from apps.common import models as common_models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


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
