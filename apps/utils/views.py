from apps.common.views import get_default_response
from apps.photo import models as photo_models
from apps.utils import models as utils_models
from apps.utils import serializers as utils_serializers
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
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
