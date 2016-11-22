from apps.account import models as account_models
from apps.common import models as common_models
from django.db import models


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


class PhotoClassification(models.Model):
    CLASSIFICATION_TYPE_CHOICES = (
        ('category', 'Category'),
        ('tag', 'Tag')
    )

    classification_type = models.CharField(max_length=32, choices=CLASSIFICATION_TYPE_CHOICES, default='tag')
    name = models.CharField(max_length=64)
    public = models.BooleanField(default=True)

    objects = PhotoClassificationManager()


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


class Photo(models.Model):
    category = models.ManyToManyField(PhotoClassification, related_name='category')
    photo_feed = models.ManyToManyField(PhotoFeed)
    tag = models.ManyToManyField(PhotoClassification, blank=True, related_name='tag')
    user = models.ForeignKey(account_models.User)
    attribution_name = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=common_models.get_uploaded_file_path)
    location = models.CharField(max_length=255, blank=True, null=True)
    photo_data = models.TextField(blank=True, null=True)
    public = models.BooleanField(default=True)
