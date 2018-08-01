from apps.common.views import get_default_response
from apps.communication.models import PushNotificationRecord
from apps.communication.serializers import AOVFCMDeviceSerializer, PushNotificationRecordSerializer
from apps.communication.tasks import send_push_notification
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from fcm_django.models import FCMDevice
from fcm_django.api.rest_framework import FCMDeviceViewSet
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_tracking.mixins import LoggingMixin


class DevicesViewSet(LoggingMixin, FCMDeviceViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = AOVFCMDeviceSerializer

    def get_queryset(self):
        """
        Return queryset of devices

        :return: Queryset
        """
        # User needs to be an admin to query this endpoint
        if not self.request.user.is_admin:
            raise PermissionDenied('You must be an admin to access this data')

        query = self.request.query_params.get('q')
        queryset = FCMDevice.objects.all()

        # If searching by user
        if query:
            queryset = queryset.filter(active=True).filter(
                Q(user__email__icontains=query) | Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) | Q(user__social_name__icontains=query) |
                Q(user__username__icontains=query))

        return queryset

    def post(self, request):
        """
        Create an FCM Device

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

            if "type" not in payload:
                data.update({"type": "ios"})

            serializer = AOVFCMDeviceSerializer(data=data, context={"request": request})

            if serializer.is_valid():
                self.perform_create(serializer)

                return get_default_response('201')
            else:
                raise ValidationError(serializer.errors)
        else:
            raise ValidationError('Missing required key "registration_id"')


class UserNotificationRecordViewSet(generics.ListCreateAPIView):
    """
        /api/users/me/notifications

        Endpoint to retrieve the notification history for a user. Serves history for 30 days prior, as anything beyond
        that is excessive
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PushNotificationRecordSerializer

    def get_queryset(self):
        """
            Method to retrieve appropriate queryset to return

        :return: QuerySet
        """

        auth_user = TokenAuthentication().authenticate(self.request)[0]
        cutoff = timezone.now() - timedelta(days=7)
        queryset = PushNotificationRecord.objects.none()
        queryset = (queryset | PushNotificationRecord.objects.filter(
            receiver__user=auth_user, created_at__gte=cutoff).order_by("-created_at") |
                    PushNotificationRecord.objects.filter(fcm_receiver__user=auth_user,
                                                          created_at__gte=cutoff).order_by("-created_at"))

        return queryset

    def post(self, request, **kwargs):
        """
            PUT Method allowing for updating the "viewed" value of the Notification Record

        :param request: HTTP Request object
        :param kwargs: Additional keyword arguments provided in the url
        :return: HTTP Response object
        """

        auth_user = TokenAuthentication().authenticate(request)[0]
        record_id = kwargs.get("record_id")
        response = get_default_response('404')
        record_entry = PushNotificationRecord.objects.none()

        record_entry = (record_entry | PushNotificationRecord.objects.filter(receiver__user=auth_user, id=record_id) |
                        PushNotificationRecord.objects.filter(fcm_receiver__user=auth_user, id=record_id))

        if record_entry.exists():
            record_entry = record_entry.first()

            record_entry.viewed = True
            record_entry.save()
            response = get_default_response('200')

        return response


@staff_member_required
def push_notification_manager(request):
    """
    View for /admin/push/

    :param request: Request object
    :return: render()
    """
    post = request.POST
    authentication = TokenAuthentication().authenticate(request)
    authenticated_user = authentication[0] if authentication else request.user

    if authenticated_user.email == "andre@nations.io":
        return HttpResponseRedirect('/admin/')

    if len(post) > 0:
        # Set up message
        message = post['message']
        recipients = post.getlist('recipient-list[]')
        # schedule = post['schedule']

        print(recipients)
        if len(message) > 0:
            if len(recipients) > 0:
                send_push_notification(message, recipients)
            else:
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
