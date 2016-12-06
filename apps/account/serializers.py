from apps.account import models
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'age', 'avatar', 'email', 'first_name', 'is_active', 'is_superuser', 'last_login', 'last_name',
                  'location', 'password', 'social_name', 'username')
        extra_kwargs = {'password': {'write_only': True}}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('user', 'bio', 'cover_image', 'gear')
