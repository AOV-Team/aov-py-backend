from apps.photo import models
from rest_framework import serializers


class PhotoClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhotoClassification
        fields = ('id', 'name', 'classification_type')


class PhotoFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhotoFeed
        fields = ('id', 'name')


class PhotoSerializer(serializers.ModelSerializer):
    dimensions = serializers.SerializerMethodField()

    def get_dimensions(self, obj):
        """
        Get image dimensions

        :param obj: Photo object
        :return: dict containing image dimensions
        """
        return {'width': obj.image.width, 'height': obj.image.height}

    class Meta:
        model = models.Photo
        fields = ('id', 'category', 'tag', 'user', 'attribution_name', 'dimensions', 'image', 'location',
                  'original_image_url', 'photo_data', 'public', 'photo_feed')
        extra_kwargs = {'public': {'default': True, 'write_only': True}}
        ordering_fields = ('id', 'location')
        ordering = ('-id',)
