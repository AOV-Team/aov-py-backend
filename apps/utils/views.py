from apps.common.mailer import send_transactional_email
from apps.common.views import get_default_response
from apps.communication.models import PushNotificationRecord
from apps.communication.tasks import send_push_notification, update_device
from apps.photo import models as photo_models
from apps.utils import models as utils_models
from apps.utils import serializers as utils_serializers
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from fcm_django.models import FCMDevice
from push_notifications.models import APNSDevice
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework_tracking.models import APIRequestLog

class APIRequestLogViewSet(generics.ListAPIView):
    """
        /api/utils/profiles
        Endpoint to retrieve a set of APIRequestLogs for a given user and time frame

    :return: List of APIRequestLog entries
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = APIRequestLog.objects.all()
    serializer_class = utils_serializers.APIRequestLogSerializer

    def get_queryset(self):
        """
            Retrieve a queryset of objects to return

        :return: Queryset
        """

        auth_user = TokenAuthentication().authenticate(self.request)[0]

        if auth_user.is_staff or auth_user.is_superuser:
            user = self.request.query_params.get("user", None)
            paths = self.request.query_params.getlist("paths", None)
            start_time = self.request.query_params.get("start_time", None)

            return APIRequestLog.objects.filter(Q(user__email=user) | Q(user__isnull=True),
                                                requested_at__gte=start_time, path__in=paths).order_by("-requested_at")
        else:
            return APIRequestLog.objects.none()


class FeedbackViewSet(generics.CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = utils_models.Feedback.objects.all()
    serializer_class = utils_serializers.FeedbackSerializer

    def post(self, request, **kwargs):
        """
            Method to submit new feedback entries to the database

        :param request: HTTP request object
        :param kwargs: Additional keyword arguments
        :return: HTTP response object
        """

        user = TokenAuthentication().authenticate(request)[0]
        feedback_id = kwargs.get("pk", None)
        feedback_type = request.data.get("feedback_type")
        response = get_default_response('400')
        update_data = {
            "user": user,
            "message": request.data.get("message"),
        }

        # Normalize the feedback type for the serializer
        if feedback_type.lower() == "appreciation":
            update_data.update({"feedback_type": "A"})

        if feedback_type.lower() == "bug":
            update_data.update({"feedback_type": "B"})

        if feedback_type.lower() == "feature request":
            update_data.update({"feedback_type": "F"})

        if feedback_id and feedback_type == "reply":
            # Check that the requesting user is staff
            if user.is_staff or user.is_superuser:
                user_feedback = utils_models.Feedback.objects.get(id=feedback_id)

                # Create a new dictionary to ensure the feedback_type
                update_data = {
                    "has_reply": True,
                    "reply_timestamp": timezone.now(),
                    "feedback_type": user_feedback.feedback_type,
                    "reply": request.data.get("reply")
                }

                if not user_feedback.has_reply:
                    serializer = utils_serializers.FeedbackSerializer(user_feedback, data=update_data, partial=True)

                    if serializer.is_valid():
                        serializer.save()
                        new_notification_sent = False

                        # Send push notification to owning user of Feedback
                        owning_apns = APNSDevice.objects.filter(user=user_feedback.user)

                        # Check for an existing FCM registry
                        fcm_device = FCMDevice.objects.filter(user=user_feedback.user)
                        if not fcm_device.exists() and owning_apns.exists():
                            fcm_token = update_device(owning_apns)
                            if fcm_token:
                                fcm_device = FCMDevice.objects.create(user=user_feedback.user,
                                                                      type="ios", registration_id=fcm_token)
                                fcm_device = FCMDevice.objects.filter(id=fcm_device.id)

                        if user_feedback.user:
                            message = "AoV has responded to your feedback. Check your associated email inbox!".format(
                                user_feedback.user.username)

                        else:
                            fcm_device = FCMDevice.objects.none()
                            owning_apns = APNSDevice.objects.none()
                            message = ""

                        # Check for record of a notification being sent for this already
                        content_type = ContentType.objects.get_for_model(utils_models.Feedback)
                        already_sent = PushNotificationRecord.objects.none()
                        already_sent = already_sent | PushNotificationRecord.objects.filter(
                            message=message, fcm_receiver__in=fcm_device, object_id=user_feedback.id, action="R",
                            content_type__pk=content_type.id)
                        already_sent = already_sent | PushNotificationRecord.objects.filter(
                            message=message, receiver__in=owning_apns, object_id=user_feedback.id, action="R",
                            content_type__pk=content_type.id)

                        if not already_sent.exists() and fcm_device.exists():
                            # To ensure we have the most recent APNSDevice entry, get a QuerySet of only the first item
                            fcm_device = FCMDevice.objects.filter(id=fcm_device.first().id)

                            # Send a push notification to the owner of the photo, letting them know they made it to AOV Picks
                            send_push_notification(message, fcm_device.values_list("id", flat=True))
                            new_notification_sent = True

                            # Delete the APNs device for easier deprecation later
                            owning_apns.delete()

                        # This check is here to make sure the record is only created for devices that we have. No APNS means no
                        # permission for notifications on the device.
                        if new_notification_sent and fcm_device.exists():
                            PushNotificationRecord.objects.create(message=message, fcm_receiver=fcm_device.first(),
                                                                  action="R",
                                                                  content_object=content_type)

                        send_transactional_email(slug="feedback-reply", user=user_feedback.user,
                                                 original=user_feedback.message, message=request.data.get("reply"))

                        response = get_default_response('200')
                        response.data = serializer.data
                    else:
                        response.data = serializer.errors
                else:
                    response = get_default_response('200')

        else:
            serializer = utils_serializers.FeedbackSerializer(data=update_data)


            if serializer.is_valid():
                serializer.save()

                # Send an email to Admins if the feedback is a but
                if feedback_type == "bug":
                    mail.mail_admins(subject="User Feedback: Bug", message=request.data.get("message"))

                response = get_default_response('200')
                response.data = serializer.data

            else:
                response.data = serializer.errors

        return response


class MeActionsViewSet(generics.CreateAPIView):
    """
    /api/me/actions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = utils_models.UserAction.objects.all()

    def post(self, request, **kwargs):
        """
        Track an action

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        payload = request.data
        response = get_default_response('400')

        if 'action' in payload and 'id' in payload:
            action = payload['action']

            # Save action
            try:
                if action == 'photo_click' or action == 'photo_imp':
                    photo = photo_models.Photo.objects.get(id=payload['id'])

                    # Save action
                    utils_models.UserAction(content_object=photo, user=authenticated_user, action=action).save()

                    response = get_default_response('200')
                else:
                    response = get_default_response('400')
                    response.data['message'] = 'Action "{}" not valid'.format(action)
            except ObjectDoesNotExist:
                response = get_default_response('404')
                response.data['message'] = 'Object with id "{}" does not exist'.format(payload['id'])

        return response
