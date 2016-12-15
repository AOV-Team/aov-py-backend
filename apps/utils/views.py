from apps.common.views import get_default_response
from apps.photo import models as photo_models
from apps.utils import models as utils_models
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication


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
