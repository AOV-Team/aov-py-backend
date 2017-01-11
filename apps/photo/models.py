from apps.account import models as account_models
from apps.common import models as common_models
from apps.photo.photo import BlurResize, WidthResize
from apps.utils import models as utils_models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.utils.safestring import mark_safe
from imagekit.models import ImageSpecField


class PhotoClassificationManager(models.Manager):
    def create_or_update(self, **kwargs):
        """
        Creates new entry or updates if PhotoClassification entry already exists

        :param kwargs:
        :return: instance of PhotoClassification
        """
        new_photo_classification = PhotoClassification(**kwargs)
        # Case insensitive
        existing = PhotoClassification.objects\
            .filter(name__iexact=new_photo_classification.name,
                    classification_type=new_photo_classification.classification_type).first()

        if existing:
            new_photo_classification.pk = existing.pk
            new_photo_classification.id = existing.id

        new_photo_classification.save()
        return new_photo_classification

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')


class PhotoClassification(models.Model):
    CLASSIFICATION_TYPE_CHOICES = (
        ('category', 'Category'),
        ('tag', 'Tag')
    )

    classification_type = models.CharField(max_length=32, choices=CLASSIFICATION_TYPE_CHOICES, default='tag')
    name = models.CharField(max_length=64)
    public = models.BooleanField(default=True)

    objects = PhotoClassificationManager()

    def __str__(self):
        return '{}: {},\tID: {}'.format(self.classification_type, self.name, self.id)

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')


class PhotoFeedManager(models.Manager):
    def create_or_update(self, **kwargs):
        """
        Creates new entry or updates if PhotoFeed entry already exists

        :param kwargs:
        :return: instance of PhotoFeed
        """
        new_photo_feed = PhotoFeed(**kwargs)
        # Case insensitive
        existing = PhotoFeed.objects.filter(name__iexact=new_photo_feed.name).first()

        if existing:
            new_photo_feed.pk = existing.pk
            new_photo_feed.id = existing.id

        new_photo_feed.save()
        return new_photo_feed


class PhotoFeed(models.Model):
    name = models.CharField(max_length=64)
    public = models.BooleanField(default=True)

    objects = PhotoFeedManager()

    def __str__(self):
        return '{},\tID: {}'.format(self.name, self.id)

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'manage', 'view')
        verbose_name = 'feed'
        verbose_name_plural = 'feeds'


class Photo(geo_models.Model):
    category = models.ManyToManyField(PhotoClassification, related_name='category')
    gear = models.ManyToManyField(account_models.Gear, blank=True)
    photo_feed = models.ManyToManyField(PhotoFeed, blank=True)
    tag = models.ManyToManyField(PhotoClassification, blank=True, related_name='tag')
    user = models.ForeignKey(account_models.User, blank=True, null=True)
    user_action = GenericRelation(utils_models.UserAction)
    user_interest = GenericRelation(account_models.UserInterest)

    attribution_name = models.CharField(max_length=255, blank=True, null=True)
    coordinates = geo_models.PointField(srid=4326, blank=True, null=True)  # Lat/long
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to=common_models.get_uploaded_file_path)
    image_blurred = ImageSpecField(source='image', processors=[BlurResize()], format='JPEG', options={'quality': 80})
    image_small = ImageSpecField(source='image', processors=[WidthResize(640)], format='JPEG')
    image_small_2 = ImageSpecField(source='image', processors=[WidthResize(750)], format='JPEG')
    image_medium = ImageSpecField(source='image', processors=[WidthResize(1242)], format='JPEG')

    location = models.CharField(max_length=255, blank=True, null=True)
    original_image_url = models.URLField(blank=True, null=True)
    photo_data = models.TextField(blank=True, null=True)
    public = models.BooleanField(default=True)

    @property
    def geo_location(self):
        pass

    @geo_location.setter
    def geo_location(self, value):
        self.coordinates = GEOSGeometry(value, srid=4326)

    @property
    def latitude(self):
        return self.coordinates.y if self.coordinates else None

    @property
    def longitude(self):
        return self.coordinates.x if self.coordinates else None

    def photo_tag(self):
        """
        Return HTML img tag with photo path

        :return: String with HTML content
        """
        return mark_safe(u'<img style="width: 100px;" src="{}">'.format(self.url_small))

    @property
    def url(self):
        """
        Image remote URL

        :return: Remote URL
        """
        return '{}{}'.format(settings.MEDIA_URL, self.image)

    @property
    def url_small(self):
        """
        Image remote URL (small version)

        :return: Remote URL
        """
        return '{}{}'.format(settings.MEDIA_URL, self.image_small)

    def __str__(self):
        return '{}:\t{},\tID: {}'\
            .format(self.user.username if self.user else self.attribution_name, self.image, self.id)

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
