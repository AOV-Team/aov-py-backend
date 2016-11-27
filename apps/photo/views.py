from apps.common.views import get_default_response, remove_pks_from_payload
from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound


class PhotoFeedViewSet(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = photo_models.PhotoFeed.objects.filter(public=True)
    serializer_class = photo_serializers.PhotoFeedSerializer


class PhotoFeedPhotosViewSet(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    def get_queryset(self, **kwargs):
        """
        Return list of photos for requested photo feed

        :return: Response object
        """
        try:
            photo_feed_id = self.kwargs['photo_feed_id']
            photo_feed = photo_models.PhotoFeed.objects.get(id=photo_feed_id)

            return photo_models.Photo.objects.filter(photo_feed=photo_feed, public=True)
        except ObjectDoesNotExist:
            raise NotFound
