from apps.common import models as common_models
from django.conf import settings
from django.db import models
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage


class RequesterManager(models.Manager):
    @staticmethod
    def create_or_update(**kwargs):
        new_requester = Requester(**kwargs)
        existing = Requester.objects.filter(email=new_requester.email).first()

        if existing:
            new_requester.created_at = existing.created_at
            new_requester.pk = existing.pk
            new_requester.id = existing.id

        new_requester.save()
        return new_requester


class Requester(common_models.EditMixin):
    """
    Model to track individual users who make a Get Featured request on AoV Web

    """
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=128)
    instagram_handle = models.CharField(
        max_length=31, null=True, blank=True, help_text="Maximum 30 characters, including the @")
    location = models.CharField(max_length=256)
    
    objects = RequesterManager()

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        verbose_name_plural = 'Requesters'

    def __str__(self):
        return "{} - {}".format(self.instagram_handle, self.full_name)


class GetFeaturedRequest(common_models.EditMixin):
    """
    Model to store the submissions of a Get Featured request

    """
    # Foreign Keys
    requester_fk = models.ForeignKey(Requester, on_delete=models.CASCADE)

    # Media fields
    image = models.ImageField(upload_to=common_models.get_uploaded_file_path, null=True, blank=True)
    audio = models.URLField(blank=True, null=True, help_text="URL to the hosted media (AWS, Soundcloud, etc.)")

    reviewed = models.BooleanField(default=False)
    story = models.TextField(null=True, blank=True)

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        verbose_name_plural = 'Get Featured Requests'

    def __str__(self):
        return "Request made by {}".format(self.requester_fk.full_name)


class CameraManager(models.Manager):
    @staticmethod
    def create_or_update(**kwargs):
        new_camera = Camera(**kwargs)
        existing = Camera.objects.filter(model=new_camera.model).first()

        if existing:
            new_camera.created_at = existing.created_at
            new_camera.pk = existing.pk
            new_camera.id = existing.id

        new_camera.save()
        return new_camera


class Camera(common_models.EditMixin):
    """
    Model to store the individual Cameras that a Requester submits in the Get Featured request

    """
    # Foreign Keys
    get_featured_request_fk = models.ForeignKey(GetFeaturedRequest, on_delete=models.CASCADE)

    model = models.CharField(max_length=156)

    objects = CameraManager()

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        verbose_name_plural = 'Cameras'

    def __str__(self):
        return self.model


class Episode(common_models.EditMixin):
    """
        A single episode of the AoV Podcast

    """
    # GENERAL
    episode_number = models.PositiveIntegerField()
    title = models.CharField(max_length=64)
    participant_social = models.CharField(max_length=31, help_text="Maximum 30 characters, including the @")
    description = models.TextField()
    quote = models.CharField(max_length=128)
    player_title_display = models.CharField(max_length=64)
    player_subtitle_display = models.CharField(max_length=64)

    # MEDIA
    audio = models.FileField(upload_to=common_models.get_podcast_file_path,
                             storage=S3Boto3Storage(bucket=settings.AWS_AUDIO_BUCKET),
                             help_text="URL to the hosted media (AWS, Soundcloud, etc.)")

    # INTERNAL
    published = models.BooleanField(default=False)
    published_date = models.DateTimeField(blank=True, null=True)
    archived = models.BooleanField(default=False)
    archive_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "AoV Podcast #{} - {}".format(self.episode_number, self.title)

    def save(self, *args, **kwargs):
        """
        Overwrite of default save to handle auto-updating of the published_date and archived_date when those flags
        change

        :param args:
        :param kwargs:
        :return:
        """
        # Check the value of published
        if self.published and not self.published_date:
            self.published_date = timezone.now()

        if self.archived and not self.archive_date:
            self.archive_date = timezone.now()

        super(Episode, self).save(*args, **kwargs)

    class META:
        default_permissions = ('add', 'change', 'delete', 'view')
        unique_together = ("episode_number", "title")
        verbose_name_plural = "Episodes"


class PodcastImage(common_models.EditMixin):
    """
    Model to store images to be used for various Podcast episodes

    """
    IMAGE_CHOICES = (
        ("EI", "Episode Image"),
        ("BI", "Background Image"),
        ("RI", "Related Image"),
        ("PI", "Player Image")
    )

    image = models.ImageField(upload_to=common_models.get_uploaded_file_path,
                              help_text="Image to be displayed below to the player on the webpage.")
    episode = models.ForeignKey("Episode", on_delete=models.CASCADE)
    display_type = models.CharField(max_length=2, choices=IMAGE_CHOICES)

    def __str__(self):
        return "{} for {}".format(self.get_display_type_display(), self.episode.title)

    class META:
        default_permissions = ('add', 'change', 'delete', 'view')
        verbose_name_plural = "Podcast Images"
