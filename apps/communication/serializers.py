from apps.account.models import User
from apps.communication import models as models
from push_notifications.api.rest_framework import APNSDeviceSerializer
from rest_framework import serializers

class AOVAPNSDeviceSerializer(APNSDeviceSerializer):
    class Meta(APNSDeviceSerializer.Meta):
        fields = ('id', 'name', 'registration_id', 'device_id', 'active', 'date_created', 'user',)


class PushNotificationRecordSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField()
    sender_avatar = serializers.SerializerMethodField()

    def get_action(self, obj):
        return obj.get_action_display()

    def get_sender_avatar(self, obj):
        if obj.action == "A":
            return None

        return PushNotificationSenderAvatarSerializer(obj.sender).data

    class Meta:
        model = models.PushNotificationRecord
        fields = ('id', 'message', 'sender_avatar', 'created_at', 'viewed', 'action', 'object_id')


class PushNotificationSenderAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar', )
