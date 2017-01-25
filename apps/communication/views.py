from apps.communication.serializers import AOVAPNSDeviceSerializer
from apps.communication.tasks import send_push_notification
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpResponseRedirect
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
        query = self.request.query_params.get('q')
        queryset = APNSDevice.objects.all()

        # If searching by user
        if query:
            queryset = queryset\
                .filter(Q(user__email__icontains=query) | Q(user__first_name__icontains=query) |
                        Q(user__last_name__icontains=query) | Q(user__social_name__icontains=query) |
                        Q(user__username__icontains=query))

        return queryset.order_by('-date_created')


@staff_member_required
def push_notification_manager(request):
    """
    View for /admin/push/

    :param request: Request object
    :return: render()
    """
    post = request.POST

    if len(post) > 0:
        # Set up message
        message = post['message']
        recipients = post.getlist('recipient-list[]')

        if len(message) > 0:
            if len(recipients) > 0:
                send_push_notification.delay(message, recipients)
            else:
                send_push_notification.delay(message, 'all')

        return HttpResponseRedirect('/admin/push/')
    else:
        pass

    context = {}

    return render(request, 'push_notification_manager.html', context)
