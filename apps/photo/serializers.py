from apps.account import models as account_models
from apps.account.serializers import UserBasicSerializer
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
    image_small_2 = serializers.ImageField(required=False)
    image_tiny_246 = serializers.ImageField(required=False)
    image_tiny_272 = serializers.ImageField(required=False)
    user_details = serializers.SerializerMethodField()

    def get_dimensions(self, obj):
        """
        Get image dimensions

        :param obj: Photo object
        :return: dict containing image dimensions
        """
        return {'width': obj.image.width, 'height': obj.image.height}

    def get_user_details(self, obj):
        """
        Get basic user details

        :param obj: Photo object
        :return: user info
        """
        user = obj.user

        if user:
            return UserBasicSerializer(obj.user).data

        return None

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset\
            .select_related('user')\
            .prefetch_related('category')\
            .prefetch_related('gear')\
            .prefetch_related('tag')

        return queryset

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
                  'image_blurred', 'image_medium', 'image_small', 'image_small_2', 'image_tiny_246', 'image_tiny_272',
                  'latitude', 'location', 'longitude', 'original_image_url', 'photo_data', 'public', 'photo_feed',
                  'user_details')
        extra_kwargs = {'original_image_url':  {'write_only': True},
                        'public': {'default': True, 'write_only': True}}
        ordering_fields = ('id', 'location')
        ordering = ('-id',)
        read_only_fields = ('image_blurred', 'image_medium', 'image_small', 'image_small_2', 'image_tiny_246',
                            'image_tiny_272', 'photo_data', 'user_details',)
