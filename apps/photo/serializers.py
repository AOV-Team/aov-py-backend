from apps.account import models as account_models
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
    gear = serializers.PrimaryKeyRelatedField(many=True, queryset=account_models.Gear.objects.all(), required=False)
    geo_location = serializers.CharField(max_length=32, write_only=True, required=False)
    image_blurred = serializers.ImageField(required=False)
    image_medium = serializers.ImageField(required=False)
    image_small = serializers.ImageField(required=False)

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
        fields = ('id', 'category', 'gear', 'geo_location', 'tag', 'user', 'attribution_name', 'dimensions', 'image',
                  'image_blurred', 'image_medium', 'image_small', 'latitude', 'location', 'longitude',
                  'original_image_url', 'photo_data', 'public', 'photo_feed')
        extra_kwargs = {'original_image_url':  {'write_only': True},
                        'public': {'default': True, 'write_only': True}}
        ordering_fields = ('id', 'location')
        ordering = ('-id',)
        read_only_fields = ('image_blurred', 'image_medium', 'image_small', 'photo_data',)
