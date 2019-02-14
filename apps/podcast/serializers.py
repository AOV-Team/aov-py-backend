from apps.podcast import models
from rest_framework import serializers


class CameraSerializer(serializers.ModelSerializer):
    """
    Serializer class for Camera objects
    """
    class Meta:
        model = models.Camera
        fields = ("model",)


class EpisodeSerializer(serializers.ModelSerializer):
    """
    Serializer class for Podcast Episodes

    """

    images = serializers.SerializerMethodField()
    audio = serializers.FileField()

    @staticmethod
    def get_images(obj):
        return EpisodePodcastImageSerializer(models.PodcastImage.objects.filter(episode=obj), many=True).data

    class Meta:
        """
        Gear is handled separately
        """
        model = models.Episode
        fields = ("episode_number", "title", "participant_social", "description", "quote", "player_title_display",
                  "player_subtitle_display", "audio", "images")


class EpisodePodcastImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = models.PodcastImage
        fields = ("image", "display_type")


class RequesterSerializer(serializers.ModelSerializer):
    """
    Serializer class for Requester objects
    """
    class Meta:
        model = models.Requester
        fields = ("email", "full_name", "instagram_handle", "location")


class GetFeaturedRequestSerializer(serializers.ModelSerializer):
    """
    Serializer Class for Get Featured Request objects
    """
    requester = RequesterSerializer()
    camera = serializers.SerializerMethodField()

    def get_camera(self, obj):
        return CameraSerializer(models.Camera.objects.filter(get_featured_request_fk=obj), many=True).data

    class Meta:
        model = models.GetFeaturedRequest
        fields = ("image", "audio", "reviewed", "story", "requester", "camera")
