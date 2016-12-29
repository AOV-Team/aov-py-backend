from apps.photo import models
from rest_framework import serializers
import re


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
    geo_location = serializers.CharField(max_length=32, write_only=True, required=False)

    def get_dimensions(self, obj):
        """
        Get image dimensions

        :param obj: Photo object
        :return: dict containing image dimensions
        """
        return {'width': obj.image.width, 'height': obj.image.height}

    def validate_geo_location(self, value):
        """
        Check that coordinates are valid
        """
        if not re.match('^POINT\s\([\-\.\d]+\s[\-\.\d]+\)$', value):
            raise serializers.ValidationError('Geo location coordinates are invalid - expecting "POINT (long lat)"')
        return value

    class Meta:
        model = models.Photo
        fields = ('id', 'category', 'geo_location', 'tag', 'user', 'attribution_name', 'dimensions', 'image', 'latitude', 'location',
                  'longitude', 'photo_data', 'public', 'photo_feed')
        extra_kwargs = {'public': {'default': True, 'write_only': True}}
        ordering_fields = ('id', 'location')
        ordering = ('-id',)
        read_only_fields = ('photo_data',)
