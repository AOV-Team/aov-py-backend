from apps.common.views import get_default_response
from apps.communication.serializers import AOVAPNSDeviceSerializer
# from apps.communication.models import PushMessage
from apps.communication.tasks import send_push_notification
# from datetime import datetime, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from push_notifications.models import APNSDevice
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated


class DevicesViewSet(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = AOVAPNSDeviceSerializer

    def get_queryset(self):
        """
        Return queryset of devices

        :return: Queryset
        """
        # User needs to be an admin to query this endpoint
        if not self.request.user.is_admin:
            raise PermissionDenied('You must be an admin to access this data')

        query = self.request.query_params.get('q')
        queryset = APNSDevice.objects.all()

        # If searching by user
        if query:
            queryset = queryset\
                .filter(active=True)\
                .filter(Q(user__email__icontains=query) | Q(user__first_name__icontains=query) |
                        Q(user__last_name__icontains=query) | Q(user__social_name__icontains=query) |
                        Q(user__username__icontains=query))

        return queryset.order_by('-date_created')

    def post(self, request):
        """
        Create an APNS Device

        :param request: Request object
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user
        payload = request.data

        if 'registration_id' in payload:
            data = {
                'user': authenticated_user.id,
                'registration_id': payload['registration_id']
            }

            serializer = AOVAPNSDeviceSerializer(data=data)

            if serializer.is_valid():
                serializer.save()

                return get_default_response('201')
            else:
                raise ValidationError(serializer.errors)
        else:
            raise ValidationError('Missing required key "registration_id"')


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
        # schedule = post['schedule']

        if len(message) > 0:
            if len(recipients) > 0:
                # send_push_notification.delay(message, recipients)
                send_push_notification(message, recipients)
            else:
                # send_push_notification.delay(message, 'all')
                send_push_notification(message, 'all')

            # Scheduling is disabled for now
            # if schedule:
            #     push_message = PushMessage(message=message, send_at=datetime.strptime(schedule, '%Y-%m-%d %H:%M'))
            #     push_message.save()
            #
            #     if len(recipients) > 0:
            #         devices = list()
            #
            #         for r in recipients:
            #             devices.append(APNSDevice.objects.get(id=r))
            #
            #         push_message.device = devices
            #         push_message.save()
            # else:
            #     if len(recipients) > 0:
            #         send_push_notification.delay(message, recipients)
            #     else:
            #         send_push_notification.delay(message, 'all')

        return HttpResponseRedirect('/admin/push/')
    else:
        pass

    context = {}

    return render(request, 'push_notification_manager.html', context)
