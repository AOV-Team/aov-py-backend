from apps.utils.models import UserAction
from rest_framework import serializers


class UserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = ('id', 'action', 'user',)
