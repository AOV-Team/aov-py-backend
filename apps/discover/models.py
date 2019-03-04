from apps.common import models as common_models
from apps.photo.models import Photo
from django.conf import settings
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


class State(models.Model):
    """
    Model representing the individual states of the United States for use on the AoV Web Discover tab
    """

    name = models.CharField(max_length=32)
    icon = models.ImageField(upload_to=common_models.get_uploaded_file_path, null=True, blank=True)
    fun_fact_1 = models.CharField(max_length=256, blank=True, null=True)
    fun_fact_2 = models.CharField(max_length=256, blank=True, null=True)
    fun_fact_3 = models.CharField(max_length=256, blank=True, null=True)
    fun_fact_4 = models.CharField(max_length=256, blank=True, null=True)
    fun_fact_5 = models.CharField(max_length=256, blank=True, null=True)
    video_url = models.URLField(null=True, blank=True)
    display = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If the state is populated with at least one fact, has an icon, and has a video URL associated to it, allow
        # it to be displayed
        if (any([self.fun_fact_1, self.fun_fact_2, self.fun_fact_3, self.fun_fact_4, self.fun_fact_5]) and self.icon
            and self.video_url):

            self.display = True

        else:
            # If the above ever fails to be met, even if it was in the past, turn of display flag
            self.display = False

        super(State, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "States"


class Sponsor(common_models.EditMixin):
    """
    Model to store information about the different individual Sponsors that will be linked to the States for the
    Discover tab on AoV Web
    """

    name = models.CharField(max_length=32)
    social_handle = models.CharField(max_length=64)
    website = models.URLField()
    downloadable_file = models.FileField(storage=S3Boto3Storage(bucket=settings.AWS_AUDIO_BUCKET),
                                         upload_to=common_models.get_uploaded_file_path)
    profile_image = models.ImageField(upload_to=common_models.get_uploaded_file_path)

    def __str__(self):
        return "{} - {}".format(self.name, self.social_handle)

    class Meta:
        verbose_name_plural = "Sponsors"


class StateSponsor(common_models.EditMixin):
    """
    Model to link individual Sponsors to a State.
    """

    sponsor = models.ForeignKey(Sponsor)
    state = models.ForeignKey(State)
    sponsorship_start = models.DateTimeField()
    sponsorship_end = models.DateTimeField()

    def __str__(self):
        return "{} sponsored by {}".format(self.sponsor.name, self.sponsor.name)

    class Meta:
        verbose_name_plural = "State Sponsors"
        unique_together = ("sponsor", "state")


class Downloader(common_models.EditMixin):
    """
    Model to store the requested information required to download the downloadable files from sponsors
    """
    name = models.CharField(max_length=64)
    email = models.EmailField()
    location = models.CharField(max_length=128)
    state_sponsor = models.ForeignKey(StateSponsor)

    def __str__(self):
        return "{} - {}".format(self.email, self.name)

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        verbose_name_plural = "Downloaders"


class Photographer(common_models.EditMixin):
    profile_image = models.ImageField(upload_to=common_models.get_uploaded_file_path)
    name = models.CharField(max_length=64)
    social_handle = models.CharField(max_length=64)

    @property
    def instagram(self):
        return "https://www.instagram.com/{}".format(self.social_handle.split("@")[1])

    def __str__(self):
        return "{} - {}".format(self.name, self.social_handle)

    class Meta:
        verbose_name_plural = "Photographers"


class StatePhotographer(common_models.EditMixin):
    """
    Model to link individual Photographers to the different States they will be featured for
    """

    photographer = models.ForeignKey(Photographer)
    state = models.ForeignKey(State)
    feature_start = models.DateTimeField()
    feature_end = models.DateTimeField()

    def __str__(self):
        return "{} featured in {}".format(self.photographer.name, self.state.name)

    class Meta:
        verbose_name_plural = "State Photographers"
        unique_together = ("photographer", "state")


class StatePhoto(common_models.EditMixin):
    """
    Model to link AoV app Photos a State on discover tab of website
    """

    state = models.ForeignKey(State)
    photo = models.ForeignKey(Photo)

    def __str__(self):
        return "Photo for {}".format(self.state.name)

    class Meta:
        verbose_name_plural = "State Photos"
        unique_together = ("photo", "state")
