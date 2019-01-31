from apps.common import models as common_models
from django.db import models


class RequesterManager(models.Manager):
    def create_or_update(self, **kwargs):
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
    requester_fk = models.ForeignKey(Requester)

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
    def create_or_update(self, **kwargs):
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
    get_featured_request_fk = models.ForeignKey(GetFeaturedRequest)

    model = models.CharField(max_length=156)

    objects = CameraManager()

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        verbose_name_plural = 'Cameras'

    def __str__(self):
        return self.model


# class Episode(common_models.EditMixin):
#     """
#         A single episode of the AoV Podcast
#
#     """
#     # MEDIA
#     # audio and metadata
#     audio = models.URLField(help_text="URL to the hosted media (AWS, Soundcloud, etc.)")

