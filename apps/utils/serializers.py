from apps.utils.models import UserAction, Feedback
from rest_framework import serializers
from rest_framework_tracking.models import APIRequestLog


class APIRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequestLog
        fields = ("id", "path", "user", "response_ms", "view")


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('user', 'id', 'feedback_type', 'message', 'reply', 'has_reply', 'reply_timestamp')


class UserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = ('id', 'action', 'user',)
