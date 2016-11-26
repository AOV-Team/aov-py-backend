from apps.account import models
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'age', 'avatar', 'email', 'first_name', 'is_active', 'is_superuser', 'last_login', 'last_name',
                  'location', 'social_name', 'username')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('bio', 'cover_image', 'gear')
