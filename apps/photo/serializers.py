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
    class Meta:
        model = models.Photo
        fields = ('id', 'category', 'tag', 'user', 'attribution_name', 'image', 'location', 'photo_data', 'public',
                  'photo_feed')
