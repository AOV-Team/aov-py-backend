from apps.common import serializers as common_serializers
from apps.discover import models
from apps.photo.serializers import PhotoSerializer
from rest_framework import serializers


class DownloadableFileOnlySerializer(serializers.ModelSerializer):
    """
    Serializer to retrieve only the downloadable file for a Sponsor
    """

    class Meta:
        model = models.Sponsor
        fields = ("downloadable_file",)

class DownloaderSerializer(serializers.ModelSerializer):
    """
    Serializer for Downloader objects
    """

    def get_downloadable_file(cls):
        return serializers.FileField(
            models.StateSponsor.objects.get(id=cls.initial_data["state_sponsor"]).sponsor.downloadable_file)

    class Meta:
        model = models.Downloader
        fields = ("id", "name", "email", "location", "state_sponsor")


class StateSerializer(serializers.ModelSerializer):
    """
    Serializer class for State objects
    """

    class Meta:
        model = models.State
        fields = ("id", "name", "fun_fact_1", "fun_fact_2", "fun_fact_3", "fun_fact_4", "fun_fact_5", "icon",
                  "video_url")

class PhotographerSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Photographer model
    """

    class Meta:
        model = models.Photographer
        fields = ("name", "instagram", "profile_image")


class SponsorSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Sponsor model
    """

    class Meta:
        model = models.Sponsor
        fields = ("name", "social_handle", "website", "profile_image")


class StatePhotographerSerializer(serializers.ModelSerializer):
    """
    Serializer class for StatePhotographer model
    """
    feature_start = common_serializers.DateTimeFieldWithTZ()
    feature_end = common_serializers.DateTimeFieldWithTZ()
    state = StateSerializer()
    photographer = PhotographerSerializer()


    class Meta:
        model = models.StatePhotographer
        fields = ("photographer", "state", "feature_start", "feature_end")


class StateSponsorSerializer(serializers.ModelSerializer):
    """
    Serializer class for StateSponsor model
    """
    sponsorship_start = common_serializers.DateTimeFieldWithTZ()
    sponsorship_end = common_serializers.DateTimeFieldWithTZ()
    state = StateSerializer()
    sponsor = SponsorSerializer()

    class Meta:
        model = models.StatePhotographer
        fields = ("sponsor", "state", "sponsorship_start", "sponsorship_end")


class StatePhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for StatePhoto model
    """

    state = StateSerializer()
    photo = PhotoSerializer()
    created_at = common_serializers.DateTimeFieldWithTZ()

    class Meta:
        model = models.StatePhoto
        fields = ("photo", "state", "created_at")
