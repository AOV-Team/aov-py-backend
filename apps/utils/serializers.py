from apps.utils.models import UserAction
from rest_framework import serializers
from rest_framework_tracking.models import APIRequestLog


class APIRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequestLog
        fields = ("id", "path", "user", "response_ms", "view")


class UserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = ('id', 'action', 'user',)
