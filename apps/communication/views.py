from apps.account.models import User
from apps.common.views import get_default_response
from apps.communication.models import PushNotificationRecord, DirectMessage, Conversation
from apps.communication.serializers import (
    AOVFCMDeviceSerializer, PushNotificationRecordSerializer, DirectMessageSerializer
)
from apps.communication.tasks import send_push_notification, update_device
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from fcm_django.api.rest_framework import FCMDeviceViewSet
from django.db import transaction
from fcm_django.models import FCMDevice
from fcm_django.fcm import FCMError
from push_notifications.models import APNSDevice
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


class DirectMessageViewSet(generics.ListCreateAPIView):
    """
    /api/users/{}/messages

    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = DirectMessageSerializer

    @transaction.atomic
    def post(self, request, **kwargs):
        """
            Method to handle the POST HTTP requests. Creates new user-to-user message objects

        :param request: HTTP Request object containing message and sender information
        :param kwargs: Additional keyword arguments used to identify the recipient of the message
        :return: HTTP Response object denoting success/failure status of the request.
        """

        # sending_user = TokenAuthentication().authenticate(request)[0]
        sending_user = User.objects.filter(id=TokenAuthentication().authenticate(request)[0].id).first()
        recipient = User.objects.filter(id=kwargs.get('pk'))

        if recipient.exists():
            recipient = recipient.first()
            # If a Conversation ID is provided, use that Conversation. Otherwise, create a new one.
            conversation_id = request.data.get("conversation_id", None)
            if conversation_id:
                conversation = Conversation.objects.get(id=conversation_id)
            else:
                conversation = Conversation.objects.create(message_count=0)
                conversation.participants = [sending_user, recipient]
                conversation.save()

            message = request.data.get("message")
            object_details = {
                "sender": sending_user,
                "recipient": recipient,
                "message": message,
                "conversation": conversation,
                "index": conversation.message_count + 1
            }

            # Create the Direct Message object
            new_message = DirectMessage.objects.create(**object_details)
            conversation.message_count = conversation.message_count + 1
            conversation.save()

            # Notify the user of the new DM
            # recipient = owning_user
            owning_apns = APNSDevice.objects.filter(user=recipient)

            # Check for an existing FCM registry
            fcm_device = FCMDevice.objects.filter(user=recipient)
            if not fcm_device.exists() and owning_apns.exists():
                fcm_token = update_device(owning_apns)
                if fcm_token:
                    fcm_device = FCMDevice.objects.create(user=recipient,
                                                          type="ios", registration_id=fcm_token)
                    fcm_device = FCMDevice.objects.filter(id=fcm_device.id)

            message = "New message from {}.".format(sending_user.username)

            # This check is here to make sure the record is only created for devices that we have. No APNS means no
            # permission for notifications on the device.
            if fcm_device.exists() and sending_user.username != recipient.username:

                try:
                    send_push_notification(message, fcm_device)
                    # Create the record of the notification being sent
                    PushNotificationRecord.objects.create(message=message, fcm_receiver=fcm_device.first(), action="D",
                                                          content_object=new_message, sender=sending_user)

                    # Delete the APNs device for easier deprecation later
                    owning_apns.delete()
                except FCMError:
                    pass

            # Serialize and return the message to the front, for display.
            serialized_message = DirectMessageSerializer(new_message)
            response = get_default_response('200')
            response.data = serialized_message.data

        else:
            response = get_default_response('400')
        return response

    def get_queryset(self):
        """
            Method to retrieve the messages in a conversation

        :return: QuerySet of DirectMessage objects in a given Conversation
        """

        sending_user = User.objects.filter(id=TokenAuthentication().authenticate(self.request)[0].id).first()
        conversation_pk = self.kwargs.get('pk')
        conversation = Conversation.objects.filter(id=conversation_pk)
        queryset = DirectMessage.objects.none()

        if conversation.exists() and sending_user.id in conversation.first().participants.values_list('id', flat=True):
            queryset = DirectMessage.objects.filter(conversation=conversation).order_by("index")

        return queryset


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
