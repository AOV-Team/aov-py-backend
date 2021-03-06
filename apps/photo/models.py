from apps.account import models as account_models
from apps.common import models as common_models
from apps.communication.models import PushNotificationRecord
from apps.communication.tasks import send_push_notification, update_device
from apps.photo.photo import BlurResize, WidthResize
from apps.utils import models as utils_models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from fcm_django.models import FCMDevice
from imagekit.models import ImageSpecField
from push_notifications.models import APNSDevice


class GalleryManager(models.Manager):
    """
        Manager class for the new Gallery model

    :author: gallen
    """

    def create_or_update(self, **kwargs):
        """
            Checks for an existing entry. If existing, update it otherwise create a new one.

        :return:
        """
        photos = kwargs.pop("photos", [])
        new_gallery = Gallery(**kwargs)
        existing = Gallery.objects.filter(name=new_gallery.name, user=new_gallery.user).first()

        if existing:
            new_gallery.pk = existing.pk
            new_gallery.created_at = existing.created_at
            new_gallery.save() # Has to occur to allow adding of objects to M2M on next lines
            new_gallery.photos.add(*existing.photos.all().values_list("id", flat=True))

        new_gallery.save()
        new_gallery.photos.add(*photos)
        new_gallery.save()
        return new_gallery


class Gallery(common_models.EditMixin):
    """
        Model representation of the Gallery database table.

    :author: gallen
    """

    name = models.CharField(max_length=32)
    photos = models.ManyToManyField("Photo", related_name="gallery_photo")
    public = models.BooleanField(default=True)
    user = models.ForeignKey(account_models.User, on_delete=models.CASCADE)

    objects = GalleryManager()

    def __str__(self):
        """
            Method to define a custom string representation of the model

        :return: String representation of the model
        """

        # return "{}: {} - {} photos".format(self.id, self.name, self.photos.all().count())

        return "{} {} - {} photos".format(self.id, self.name, 0)

    class Meta:
        verbose_name_plural = "Galleries"


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
            new_photo_classification.photo_feed = existing.photo_feed
            new_photo_classification.category_image = existing.category_image
            new_photo_classification.icon = existing.icon
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

    category_image = models.ImageField(
        upload_to=common_models.get_classification_background_file_path, blank=True, null=True)
    classification_type = models.CharField(max_length=32, choices=CLASSIFICATION_TYPE_CHOICES, default='tag')
    icon = models.ImageField(upload_to=common_models.get_classification_icon_file_path, blank=True, null=True)
    name = models.CharField(max_length=512)
    photo_feed = models.ForeignKey('PhotoFeed', on_delete=models.SET_NULL, null=True, blank=True)
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
    photo_limit = models.IntegerField(blank=True, null=True, verbose_name='max photos to display',
                                      help_text='Leave blank for unlimited.',
                                      validators=[MaxValueValidator(9999)])
    public = models.BooleanField(default=True)
    randomize = models.BooleanField(default=False)

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
    user = models.ForeignKey(account_models.User, blank=True, null=True, related_name="photo_user", on_delete=models.SET_NULL)
    user_action = GenericRelation(utils_models.UserAction)
    user_interest = GenericRelation(account_models.UserInterest)

    attribution_name = models.CharField(max_length=255, blank=True, null=True)
    coordinates = geo_models.PointField(srid=4326, blank=True, null=True)  # Lat/long
    created_at = models.DateTimeField(auto_now_add=True)
    aov_feed_add_date = models.DateTimeField(null=True, blank=True)

    image = models.ImageField(upload_to=common_models.get_uploaded_file_path)
    image_tiny_246 = ImageSpecField(source='image', processors=[WidthResize(246)], format='JPEG')
    image_tiny_272 = ImageSpecField(source='image', processors=[WidthResize(272)], format='JPEG')
    image_blurred = ImageSpecField(source='image', processors=[BlurResize()], format='JPEG', options={'quality': 80})
    image_small = ImageSpecField(source='image', processors=[WidthResize(640)], format='JPEG')
    image_small_2 = ImageSpecField(source='image', processors=[WidthResize(750)], format='JPEG')
    image_medium = ImageSpecField(source='image', processors=[WidthResize(1242)], format='JPEG')

    location = models.CharField(max_length=255, blank=True, null=True)
    magazine_authorized = models.BooleanField(default=True)
    original_image_url = models.URLField(blank=True, null=True)
    public = models.BooleanField(default=True)
    votes = models.IntegerField(default=0)

    # Behind the Shot
    photo_data = models.TextField(blank=True, null=True)
    bts_lens = models.CharField(blank=True, null=True, max_length=256)
    bts_shutter = models.CharField(blank=True, null=True, max_length=256)
    bts_iso = models.CharField(blank=True, null=True, max_length=256)
    bts_aperture = models.CharField(blank=True, null=True, max_length=256)
    bts_camera_settings = models.CharField(blank=True, null=True, max_length=256)
    bts_time_of_day = models.CharField(blank=True, null=True, max_length=256)
    bts_photo_editor = models.CharField(blank=True, null=True, max_length=256)
    bts_camera_make = models.CharField(blank=True, null=True, max_length=256)
    bts_camera_model = models.CharField(blank=True, null=True, max_length=256)
    caption = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        new_notification_sent = False
        if hasattr(self.user, "id"):
            owning_user = account_models.User.objects.filter(id=self.user.id).first()
            owning_apns = APNSDevice.objects.filter(user=owning_user)

            # Check for an existing FCM registry
            fcm_device = FCMDevice.objects.filter(user=owning_user)
            if not fcm_device.exists() and owning_apns.first():
                fcm_token = update_device(owning_apns)
                if fcm_token:
                    fcm_device = FCMDevice.objects.create(user=owning_user,
                                                          type="ios", registration_id=fcm_token)
                    fcm_device = FCMDevice.objects.filter(id=fcm_device.id)


            if owning_user:
                message = "Your artwork has been featured in the AOV Picks gallery, {}!".format(owning_user.username)

        else:
            fcm_device = FCMDevice.objects.none()
            owning_apns = APNSDevice.objects.none()
            message = ""

        try:
            # AOV Picks is the name of the feed that is curated by Prince. Set the add_date field for proper ordering
            if "AOV Picks" in self.photo_feed.all().values_list("name", flat=True):
                if not self.aov_feed_add_date:
                    self.aov_feed_add_date = timezone.now()

                    # Check for record of a notification being sent for this already
                    photo_type = ContentType.objects.get_for_model(self)
                    already_sent = PushNotificationRecord.objects.none()
                    already_sent = already_sent | PushNotificationRecord.objects.filter(
                        message=message, fcm_receiver__in=fcm_device, object_id=self.id, action="A",
                        content_type__pk=photo_type.id)
                    already_sent = already_sent | PushNotificationRecord.objects.filter(message=message,
                                                                                        receiver__in=owning_apns,
                                                                                        object_id=self.id, action="A",
                                                                                        content_type__pk=photo_type.id)

                    if not already_sent.exists() and fcm_device.exists():
                        # To ensure we have the most recent APNSDevice entry, get a QuerySet of only the first item
                        fcm_device = FCMDevice.objects.filter(id=fcm_device.first().id)

                        # Send a push notification to the owner of the photo, letting them know they made it to AOV Picks
                        send_push_notification(message, fcm_device.values_list("id", flat=True))
                        new_notification_sent = True

                        # Delete the APNs device for easier deprecation later
                        owning_apns.delete()

            else:
                self.aov_feed_add_date = None
        except ValueError:
            pass

        # This check is here to make sure the record is only created for devices that we have. No APNS means no
        # permission for notifications on the device.
        if new_notification_sent and fcm_device.exists():
            PushNotificationRecord.objects.create(message=message, fcm_receiver=fcm_device.first(), action="A",
                                                  content_object=self)
        super(Photo, self).save(*args, **kwargs)

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


class PhotoCommentManager(geo_models.Manager):
    """
        Manager to define a create_or_update method for the PhotoComment model class

    :author: gallen
    """

    def create_or_update(self, **kwargs):
        """
            Method that checks for an existing entry in the table. If there is on, updates it.

        :param kwargs: Dictionary containing values to create a new PhotoComment object
        :return: Saved instance of a PhotoComment
        """
        # Create a new PhotoComment
        new_photo_comment = PhotoComment(**kwargs)

        # check for an existing entry with the same content, user, and photo_id
        existing = PhotoComment.objects.filter(user_id=new_photo_comment.user_id,
                                               photo_id=new_photo_comment.photo_id,
                                               comment=new_photo_comment.comment,
                                               parent_id=new_photo_comment.parent_id).first()

        if existing:
            new_photo_comment.pk = existing.pk
            new_photo_comment.id = existing.id
            new_photo_comment.created_at = existing.created_at
            new_photo_comment.modified_at = timezone.now()

        new_photo_comment.save()
        return new_photo_comment


class PhotoComment(common_models.GeoEditMixin):
    """
        Model for users' comments on a photo

    :author: gallen
    """

    photo = models.ForeignKey(Photo, related_name="photo_comment", on_delete=models.CASCADE)
    comment = models.TextField()
    parent = models.ForeignKey("self", null=True, related_name="replies", on_delete=models.SET_NULL)
    user = models.ForeignKey(account_models.User, related_name="photo_comment_user", on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)
    mentions = ArrayField(base_field=models.CharField(max_length=255, blank=True), blank=True, null=True)

    objects = PhotoCommentManager()

    class Meta:
        verbose_name_plural = "Photo Comments"


class PhotoVoteManager(models.Manager):
    """
        Manage class to define a create_or_update method for PhotoVote objects
        
    :author: gallen
    """
    
    def create_or_update(self, **kwargs):
        new_photo_vote = PhotoVote(**kwargs)
        existing = PhotoVote.objects.filter(photo=new_photo_vote.photo, user=new_photo_vote.user).first()
        
        if existing:
            new_photo_vote.pk = existing.pk
            new_photo_vote.id = existing.id
            new_photo_vote.created_at = existing.created_at
            new_photo_vote.modified_at = timezone.now()

        new_photo_vote.save()
        return new_photo_vote


class PhotoVote(common_models.EditMixin):
    """
        Model to track who has voted on what images

    :author: gallen
    """

    photo = models.ForeignKey(Photo, related_name="photo_vote", on_delete=models.CASCADE)
    upvote = models.BooleanField(default=False)
    user = models.ForeignKey(account_models.User, on_delete=models.CASCADE)

    objects = PhotoVoteManager()

    class Meta:
        verbose_name_plural = "Photo Vote Records"
