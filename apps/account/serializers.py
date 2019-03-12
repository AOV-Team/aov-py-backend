from apps.account import models
from rest_framework import serializers
import re


class AOVWebUserSerializer(serializers.ModelSerializer):
    """ This serializer is for publicly consumable web based requests"""

    class Meta:
        model = models.User
        fields = ("id", "age", "first_name", "last_name", "location", "social_name", "username", "avatar",)


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


class BlockedSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer()
    blocked_by = serializers.PrimaryKeyRelatedField(queryset=models.Gear.objects.all())

    class Meta:
        model = models.Blocked
        fields = ('user', 'blocked_by',)
        read_only_fields = ('user', 'blocked_by',)


class UserSerializer(serializers.ModelSerializer):
    gear = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Gear.objects.all(), required=False)

    class Meta:
        model = models.User
        fields = ('id', 'age', 'avatar', 'email', 'first_name', 'gear', 'gender', 'is_active', 'is_admin', 'last_login',
                  'last_name', 'location', 'password', 'social_name', 'social_url', 'username', 'website_url',
                  'signup_source',)
        read_only_fields = ('is_admin', 'last_login',)
        extra_kwargs = {'is_active': {'default': True, 'write_only': True}, 'password': {'write_only': True},
                        'signup_source': {'write_only': True}}


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


class UserLocationSerializer(serializers.ModelSerializer):
    geo_location = serializers.CharField(max_length=32, write_only=True, required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.all(), required=True)

    def validate_geo_location(self, value):
        """
        Check that coordinates are valid
        """
        if not re.match('^POINT\s\([\-\.\d]+\s[\-\.\d]+\)$', value):
            raise serializers.ValidationError('Geo location coordinates are invalid - expecting "POINT (long lat)"')
        return value

    class Meta:
        model = models.UserLocation
        fields = ('id', 'geo_location', 'user', 'latitude', 'location', 'longitude', 'coordinates')
        ordering_fields = ('id', 'location')
        ordering = ('-id',)
