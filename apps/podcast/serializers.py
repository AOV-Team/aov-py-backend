from apps.podcast import models
from rest_framework import serializers


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