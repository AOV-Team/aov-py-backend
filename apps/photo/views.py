from apps.common.views import get_default_response, remove_pks_from_payload
from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound, ValidationError


class PhotoClassificationViewSet(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoClassificationSerializer

    def get_queryset(self):
        """
        Return classifications

        :return: Response object
        """
        query_params = {
            'public': True
        }

        classification_type = self.request.query_params.get('classification', None)

        # Add classification if provided
        if classification_type:
            if classification_type == 'category' or classification_type == 'tag':
                query_params['classification_type'] = classification_type
            else:
                # HTTP 400
                raise ValidationError('Classification type "{}" not valid'.format(classification_type))

        return photo_models.PhotoClassification.objects.filter(**query_params)

    def post(self, request, *args, **kwargs):
        """
        Create new classification

        :param request: Request object
        :param args:
        :param kwargs:
        :return: Response object
        """
        payload = request.data

        payload = remove_pks_from_payload('photo_classification', payload)

        # Only tads are allowed
        if 'classification_type' in payload:
            if payload['classification_type'] == 'category':
                raise ValidationError('Cannot create a category')
        else:
            payload['classification_type'] = 'tag'

        # If trying to create private entry, deny
        if 'public' in payload:
            if not payload['public']:
                raise ValidationError('Cannot create private classification')

        serializer = photo_serializers.PhotoClassificationSerializer(data=payload)

        if serializer.is_valid():
            # If classification already exists, update.
            # Else save new
            try:
                classification = photo_models.PhotoClassification.objects.get(name__iexact=payload['name'],
                                                                              classification_type='tag')

                serializer.update(classification, serializer.validated_data)
            except ObjectDoesNotExist:
                serializer.save()

            response = get_default_response('200')
            response.data = serializer.data
            return response
        else:
            raise ValidationError(serializer.errors)


class PhotoClassificationPhotosViewSet(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    def get_queryset(self):
        """
        Return photos for a classification

        :return: Queryset
        """
        try:
            photo_classification_id = self.kwargs.get('photo_classification_id')
            classification = photo_models.PhotoClassification.objects.get(id=photo_classification_id)

            return photo_models.Photo.objects.filter(Q(category=classification) | Q(tag=classification), public=True)
        except ObjectDoesNotExist:
            raise NotFound


class PhotoFeedViewSet(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = photo_models.PhotoFeed.objects.filter(public=True)
    serializer_class = photo_serializers.PhotoFeedSerializer


class PhotoFeedPhotosViewSet(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    def get_queryset(self):
        """
        Return list of photos for requested photo feed

        :return: Queryset
        """
        try:
            photo_feed_id = self.kwargs['photo_feed_id']
            photo_feed = photo_models.PhotoFeed.objects.get(id=photo_feed_id)

            return photo_models.Photo.objects.filter(photo_feed=photo_feed, public=True)
        except ObjectDoesNotExist:
            raise NotFound
