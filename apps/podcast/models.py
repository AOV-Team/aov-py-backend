from apps.common import models as common_models
from django.db import models

class Requester(common_models.EditMixin):
    """
    Model to track individual users who make a Get Featured request on AoV Web

    """
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=128)
    instagram_handle = models.CharField(
        max_length=31, null=True, blank=True, help="Maximum 30 characters, including the @")
    location = models.CharField(max_length=256)

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        verbose_name_plural = 'Requesters'


class GetFeaturedRequest(common_models.EditMixin):
    """
    Model to store the submissions of a Get Featured request

    """
    # Foreign Keys
    requester_fk = models.ForeignKey(Requester)

    # Media fields
    image = models.ImageField(upload_to=common_models.get_uploaded_file_path, null=True, blank=True)
    # audio = models.FileField(upload_to=common_models.get_audio_file_path)




class Camera(common_models.EditMixin):
    """
    Model to store the individual Cameras that a Requester submits in the Get Featured request

    """
    # Foreign Keys
    get_featured_request_fk = models.ForeignKey(GetFeaturedRequest)

    model = models.CharField(max_length=156)

