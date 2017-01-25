from apps.communication.serializers import AOVAPNSDeviceSerializer
from apps.communication.tasks import send_push_notification
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from push_notifications.models import APNSDevice
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser


class DevicesViewSet(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAdminUser,)
    serializer_class = AOVAPNSDeviceSerializer

    def get_queryset(self):
        """
        Return queryset of devices

        :return: Queryset
        """
        return APNSDevice.objects.all().order_by('-date_created')


@staff_member_required
def push_notification_manager(request):
    """
    View for /admin/push/

    :param request: Request object
    :return: render()
    """
    post = request.POST

    if len(post) > 0:
        print(post)
        # Set up message
        message = post['message']
        recipients = post['recipients']

        if recipients == 'all':
            send_push_notification.delay(message, 'all')
    else:
        pass

    context = {}

    return render(request, 'push_notification_manager.html', context)
