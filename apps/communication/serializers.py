from push_notifications.api.rest_framework import APNSDeviceSerializer


class AOVAPNSDeviceSerializer(APNSDeviceSerializer):
    class Meta(APNSDeviceSerializer.Meta):
        fields = ('id', 'name', 'registration_id', 'device_id', 'active', 'date_created',)
