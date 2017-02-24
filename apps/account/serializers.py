from apps.account import models
from rest_framework import serializers


class GearSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Gear
        fields = ('id', 'item_make', 'item_model', 'link', 'public', 'reviewed',)
        extra_kwargs = {'public': {'default': True, 'write_only': True}}


class UserBasicSerializer(serializers.ModelSerializer):
    """ Use this serializer to add additional user info to photos """
    class Meta:
        model = models.User
        fields = ('id', 'age', 'email', 'first_name', 'last_name', 'location', 'social_name', 'username',)


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'age', 'avatar', 'email', 'first_name', 'gear', 'last_name', 'location', 'social_name',
                  'social_url', 'username', 'website_url',)


class UserSerializer(serializers.ModelSerializer):
    gear = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Gear.objects.all(), required=False)

    class Meta:
        model = models.User
        fields = ('id', 'age', 'avatar', 'email', 'first_name', 'gear', 'is_active', 'is_admin', 'last_login',
                  'last_name', 'location', 'password', 'social_name', 'social_url', 'username', 'website_url',)
        read_only_fields = ('is_admin', 'last_login',)
        extra_kwargs = {'is_active': {'default': True, 'write_only': True}, 'password': {'write_only': True}}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Gear is handled separately
        """
        model = models.Profile
        fields = ('user', 'bio', 'cover_image')


class UserInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInterest
        fields = ('id', 'interest_type')
