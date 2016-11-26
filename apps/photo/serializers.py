from apps.photo import models
from rest_framework import serializers


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Photo
        fields = ('id', 'category', 'tag', 'user', 'attribution_name', 'image', 'location', 'photo_data', 'public',
                  'photo_feed')
