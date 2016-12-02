from apps.common import models as common_models
from apps.common.views import get_default_response, handle_jquery_empty_array, remove_pks_from_payload
from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from apps.photo.photo import Photo
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError


@staff_member_required
def photo_admin(request):
    """
    View for /admin/photos

    :param request: Request object
    :return: render()
    """
    photos = photo_models.Photo.objects.filter(public=True).order_by('-id')

    # Add list of names of feeds that image is in
    # Makes it easier to work with in the HTML template
    for photo in photos:
        if not getattr(photo, 'photo_feed_names', None):
            photo.photo_feed_names = list()

        for feed in photo.photo_feed.all():
            if feed.public:
                photo.photo_feed_names.append(feed.name)

    context = {
        'media_url': settings.MEDIA_URL,
        'photo_feeds': photo_models.PhotoFeed.objects.filter(public=True),
        'photos': photos
    }

    return render(request, 'photos.html', context)


class PhotoViewSet(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    def get_queryset(self):
        """
        Return images

        :return: Queryset
        """
        classification_param = self.request.query_params.get('classification')
        location = self.request.query_params.get('location')
        query_params = {
            'public': True
        }

        if location:
            query_params['location__iexact'] = location

        if classification_param:
            try:
                # If we get classification id, use it
                # Otherwise set to 0 (will not match anything)
                try:
                    classification_id_param = int(classification_param)
                except ValueError:
                    classification_id_param = 0

                # Match either by ID or name
                classification = photo_models.PhotoClassification.objects\
                    .get(Q(id=classification_id_param) | Q(name__iexact=classification_param))

                return photo_models.Photo.objects\
                    .filter(Q(category=classification) | Q(tag=classification), **query_params).order_by('-id')
            except ObjectDoesNotExist:
                # Empty queryset
                return photo_models.Photo.objects.none()
        else:
            return photo_models.Photo.objects.filter(**query_params).order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Save photo

        :param request: Request object
        :param args:
        :param kwargs:
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        payload = request.data
        payload['user'] = authenticated_user.id

        # Image compression
        # Save original first
        if 'image' in payload:
            # Save original photo to media
            photo = Photo(payload['image'])
            photo.save('{}/u{}_{}_{}'
                       .format(settings.MEDIA_ROOT, authenticated_user.id, common_models.get_date_stamp_str(),
                               photo.name))

            # Process image to save
            payload['image'] = photo.compress()

        serializer = photo_serializers.PhotoSerializer(data=payload)

        if serializer.is_valid():
            serializer.save()

            response = get_default_response('200')
            response.data = serializer.data
        else:
            raise ValidationError(serializer.errors)

        return response


class PhotoClassificationViewSet(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoClassificationSerializer

    def get_queryset(self):
        """
        Return classifications

        :return: Queryset
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

        # Only tags are allowed
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
    authentication_classes = (SessionAuthentication, TokenAuthentication)
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


class PhotoSingleViewSet(generics.RetrieveDestroyAPIView, generics.UpdateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = photo_models.Photo.objects.all()
    serializer_class = photo_serializers.PhotoSerializer

    def delete(self, request, *args, **kwargs):
        """
        Delete a photo

        :param request: Request object
        :param args:
        :param kwargs:
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        photo_id = kwargs.get('pk')

        try:
            photo = photo_models.Photo.objects.get(id=photo_id, public=True)

            # Photo must belong to authenticated user
            if photo.user == authenticated_user:
                photo.public = False
                photo.save()

                response = get_default_response('200')
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            raise NotFound

        return response

    def get(self, request, *args, **kwargs):
        """
        Get a photo

        :param request: Request object
        :return: Response object
        """
        photo_id = kwargs.get('pk')

        try:
            photo = photo_models.Photo.objects.get(id=photo_id, public=True)

            response = get_default_response('200')
            response.data = photo_serializers.PhotoSerializer(photo).data
        except ObjectDoesNotExist:
            raise NotFound

        return response

    def patch(self, request, *args, **kwargs):
        """

        :param request:
        :return:
        """
        # Needs to be superuser
        if request.user.is_superuser:
            photo_id = kwargs.get('pk')
            payload = request.data
            payload = remove_pks_from_payload('photo', payload)
            payload = handle_jquery_empty_array('photo_feed', payload)

            # Cannot change image
            if 'image' in payload:
                del payload['image']

            try:
                photo = photo_models.Photo.objects.get(id=photo_id)
                serializer = photo_serializers.PhotoSerializer(photo, data=payload, partial=True)

                if serializer.is_valid():
                    serializer.save()

                    response = get_default_response('200')
                    response.data = serializer.data
                    return response
                else:
                    raise ValidationError(serializer.errors)
            except ObjectDoesNotExist:
                raise NotFound
        else:
            raise PermissionDenied
