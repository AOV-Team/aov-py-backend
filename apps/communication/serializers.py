from apps.account.models import User
from apps.account.serializers import UserPublicSerializer
from apps.common.serializers import DateTimeFieldWithTZ
from apps.communication import models as models
from apps.photo.models import Photo
from apps.photo.serializers import PhotoSerializer
from fcm_django.api.rest_framework import FCMDeviceSerializer
from push_notifications.api.rest_framework import APNSDeviceSerializer
from rest_framework import serializers

class AOVAPNSDeviceSerializer(APNSDeviceSerializer):
    class Meta(APNSDeviceSerializer.Meta):
        fields = ('id', 'name', 'registration_id', 'device_id', 'active', 'date_created', 'user',)


class AOVFCMDeviceSerializer(FCMDeviceSerializer):
    class Meta(FCMDeviceSerializer.Meta):
        fields = (
            "id", "name", "registration_id", "device_id", "active",
            "date_created", "type", "user"
        )
        extra_kwargs = {"user": {"read_only": True, "required": True}}


class ConversationSerializer(serializers.ModelSerializer):
    latest = serializers.SerializerMethodField()
    participants = UserPublicSerializer(many=True)

    def get_latest(self, obj):
        message = models.DirectMessage.objects.filter(conversation=obj, index=obj.message_count)
        if message.exists():
            return DirectMessageSerializer(message.first()).data
        return {}

    class Meta:
        model = models.Conversation
        fields = ("id", "participants", "latest", "message_count")


class DirectMessageSerializer(serializers.ModelSerializer):
    conversation = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = DateTimeFieldWithTZ()

    class Meta:
        model = models.DirectMessage
        fields = ("id", "sender", "recipient", "message", "index", "conversation", "created_at", "read")


class PushNotificationRecordSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    related_object = serializers.SerializerMethodField()

    def get_action(self, obj):
        return obj.get_action_display()

    def get_related_object(self, obj):
        if obj.action == "F":
            return PushNotificationSenderSerializer(User.objects.filter(id=obj.object_id), many=True).data

        elif obj.action in ["A", "C", "T", "U"]:
            return PhotoSerializer(
                Photo.objects.filter(id=obj.object_id), many=True, context={"request": self.context["request"]}).data

        elif obj.action == "D":
            return DirectMessageSerializer(models.DirectMessage.objects.filter(id=obj.object_id), many=True).data

    def get_sender(self, obj):
        if obj.action == "A":
            return None

        return PushNotificationSenderSerializer(obj.sender).data

    class Meta:
        model = models.PushNotificationRecord
        fields = ('id', 'message', 'sender', 'created_at', 'viewed', 'action', 'related_object')


class PushNotificationSenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'age', 'avatar', 'email', 'first_name', 'gear', 'last_name', 'location', 'social_name',
                  'social_url', 'username', 'website_url')
