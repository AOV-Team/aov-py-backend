from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token


class PhotoFeedViewSet(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = photo_models.PhotoFeed.objects.filter(public=True)
    serializer_class = photo_serializers.PhotoFeedSerializer
