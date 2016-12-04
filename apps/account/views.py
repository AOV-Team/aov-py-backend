from apps.account import models as account_models
from apps.account import serializers as account_serializers
from apps.account import tasks as account_tasks
from apps.common import models as common_models
from apps.common.views import get_default_response, remove_pks_from_payload
from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from apps.photo.photo import Photo
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from social.apps.django_app.utils import load_strategy
from social.apps.django_app.utils import load_backend
from social.exceptions import AuthAlreadyAssociated


class AuthenticateViewSet(APIView):
    """
    /api/auth
    """
    permission_classes = (permissions.AllowAny,)
    queryset = account_models.User.objects.all()
    serializer_class = photo_serializers.PhotoSerializer

    def delete(self, request):
        """
        Delete token to log user out

        :param request: Request object
        :return: Response object
        """
        response = get_default_response('200')

        try:
            authenticated_token = TokenAuthentication().authenticate(request)[1]
            authenticated_token.delete()
        except TypeError:
            response = get_default_response('401')
            response.data['message'] = 'User not logged in'
            response.data['userMessage'] = 'Cannot log out you - you are not logged in!'

        return response

    def post(self, request):
        """
        Log a user in
        :param request: Request object
        :return: Response object
        """
        payload = request.data
        email = payload.get('email')
        password = payload.get('password')
        response = get_default_response('400')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                # User exists and is active, get/create token and return
                if user.is_active:
                    token = Token.objects.get_or_create(user=user)
                    response = get_default_response('201')
                    response.data['token'] = token[0].key
                else:
                    response = get_default_response('403')
                    response.data['message'] = 'User inactive'
                    response.data['userMessage'] = 'Cannot log you in because your user is inactive'
            else:
                response = get_default_response('401')
                response.data['message'] = 'Authentication failed'
                response.data['userMessage'] = 'Email or password incorrect. Please try again.'

        return response


class MeViewSet(generics.RetrieveAPIView, generics.UpdateAPIView):
    """
    /api/me
    Endpoint for retrieving user info
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.User.objects.all()

    def get(self, request):
        """
        Get user

        :param request: Request object
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]

        response = get_default_response('200')
        response.data = account_serializers.UserSerializer(authenticated_user).data

        return response

    def patch(self, request):
        """
        Update user

        :param request: Request object
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        payload = request.data
        response = get_default_response('200')

        # Remove PKs and other fields that cannot be updated via API
        payload = remove_pks_from_payload('user', payload)

        if 'email' in payload:
            del payload['email']

        if 'is_active' in payload:
            del payload['is_active']

        if 'is_superuser' in payload:
            del payload['is_superuser']

        if 'username' in payload:
            del payload['username']

        updated_user = account_models.User.objects.get(id=authenticated_user.id)

        # Update user
        for key in payload:
            setattr(updated_user, key, payload[key])

        updated_user.save()

        response.data = account_serializers.UserSerializer(updated_user).data

        return response


class MeProfileViewSet(generics.RetrieveAPIView):
    """
    api/me/profile
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.Profile.objects.all()

    def get(self, request):
        """
        GET user profile

        :param request: Request object
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        response = get_default_response('404')

        try:
            profile = account_models.Profile.objects.get(user=authenticated_user)

            response = get_default_response('200')
            response.data = account_serializers.ProfileSerializer(profile).data
        except ObjectDoesNotExist:
            response.data['message'] = 'Profile does not exist.'
            response.data['userMessage'] = 'You do not have a profile.'

        return response

    def patch(self, request):
        """
        PATCH user profile

        :param request: Request object
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        payload = request.data
        response = get_default_response('404')

        # Look for profile and update entry if profile exists
        # ELSE return 404
        try:
            profile = account_models.Profile.objects.get(user=authenticated_user)

            # Remove PKs that cannot be updated via API
            payload = remove_pks_from_payload('profile', payload)
            payload = remove_pks_from_payload('user', payload)
            payload['user'] = authenticated_user.id

            # Image compression
            # Save original first
            if 'cover_image' in payload:
                # Save original photo to media
                try:
                    photo = Photo(payload['cover_image'])
                    photo.save('COVER_u{}_{}_{}'
                               .format(authenticated_user.id, common_models.get_date_stamp_str(), photo.name),
                               custom_bucket=settings.STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'])

                    # Process image to save
                    payload['cover_image'] = photo.compress()
                except TypeError:
                    raise ValidationError('Cover image is not of type image')

            serializer = account_serializers.ProfileSerializer(data=payload, partial=True)

            if serializer.is_valid():
                serializer.update(profile, serializer.validated_data)

                response = get_default_response('200')
                response.data = serializer.data
            else:
                response = get_default_response('400')
                response['message'] = serializer.errors
        except ObjectDoesNotExist:
            response.data['message'] = 'Profile does not exist.'
            response.data['userMessage'] = 'You do not have a profile.'

        return response

    def post(self, request):
        """
        CREATE (POST) user profile

        :param request: Request object
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        payload = request.data
        response = get_default_response('400')

        if 'bio' in payload or 'cover_image' in payload or 'gear' in payload:
            # Clean up and assign user
            payload = remove_pks_from_payload('profile', payload)
            payload = remove_pks_from_payload('user', payload)
            payload['user'] = authenticated_user.id

            # Image compression
            # Save original first
            if 'cover_image' in payload:
                # Save original photo to media
                try:
                    photo = Photo(payload['cover_image'])
                    photo.save('COVER_u{}_{}_{}'
                               .format(authenticated_user.id, common_models.get_date_stamp_str(), photo.name),
                               custom_bucket=settings.STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'])

                    # Process image to save
                    payload['cover_image'] = photo.compress()
                except TypeError:
                    raise ValidationError('Cover image is not of type image')

            serializer = account_serializers.ProfileSerializer(data=payload)

            if serializer.is_valid():
                serializer.save()

                response = get_default_response('200')
                response.data = serializer.data
            else:
                response.data['message'] = serializer.errors

        return response


class SampleTasksViewSet(APIView):
    """
    Class for api/sample_tasks
    """
    permission_classes = (permissions.AllowAny, )

    @staticmethod
    def get(request, **kwargs):
        """
        Not implemented
        :param request: request object
        :param kwargs: additional parameters
        :return: Response object
        """
        # NOT IMPLEMENTED, return 501!
        return get_default_response('501')

    @staticmethod
    def post(request):
        """
        POST /api/sample_tasks to create a sample Celery task.
        Use Flower to view result
        :param request: HTTP request object
        :return: Response object
        """
        payload = request.data
        value = payload.get('value', None)
        response = get_default_response('400')

        if value:
            # Pass value to task queue
            account_tasks.test_task.apply_async(args=[value], )

            # Prepare response
            response = get_default_response('201')
            response['message'] = 'Task has been accepted and is being processed.'
            response['userMessage'] = 'Your task is currently being processed.'

        return response


class SocialSignUpViewSet(generics.CreateAPIView):
    """
    View set for signing up user using third party OAuth

    """
    permission_classes = (permissions.AllowAny,)
    queryset = account_models.User.objects.all()
    serializer_class = account_serializers.UserSerializer

    def create(self, request):
        """
        POST method to authenticate a user via third party OAuth and then create a user if doesn't already exist
        See link for more info:
        https://yeti.co/blog/social-auth-with-django-rest-framework/

        :param request: Request object
        :return: Response object
        """
        payload = request.data
        access_token = payload.get('access_token', None)
        provider = payload.get('provider', 'facebook')
        response = get_default_response('400')

        if access_token:
            # Social auth stuffs
            strategy = load_strategy(request)
            backend = load_backend(strategy, provider, None)

            try:
                user = backend.do_auth(access_token)

                if user:
                    token = Token.objects.get_or_create(user=user)

                    response = get_default_response('200')
                    response.data['message'] = 'User "{}" successfully authenticated.'.format(user.email)
                    response.data['userMessage'] = 'You have been authenticated!'
                    response.data['token'] = token[0].key
            except AuthAlreadyAssociated:
                response = get_default_response('409')
                response.data['message'] = 'User already exists'
                response.data['userMessage'] = 'The specified user already exists. Please log in.'

        return response


class UserPhotosViewSet(generics.ListAPIView):
    """
    /api/users/{}/photos
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = photo_models.Photo.objects.all()
    serializer_class = photo_serializers.PhotoSerializer

    def get(self, request, **kwargs):
        """
        Get user's photos

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]

        photos = photo_models.Photo.objects.filter(user=authenticated_user, public=True).order_by('-id')
        paginated_photos = self.paginate_queryset(photos)

        serialized_items = list()

        for photo in paginated_photos:
            serialized_items.append(photo_serializers.PhotoSerializer(photo).data)

        response = self.get_paginated_response(serialized_items)

        return response


class UserViewSet(generics.CreateAPIView):
    """
    /api/user
    Endpoint class for User model
    """
    permission_classes = (permissions.AllowAny,)
    queryset = account_models.User.objects.all()
    serializer_class = account_serializers.UserSerializer

    def post(self, request):
        """
        Create a new user

        :param request: Request object
        :return: Response object
        """
        payload = request.data
        response = get_default_response('400')

        if 'avatar' in payload:
            # Save original photo to media
            try:
                photo = Photo(payload['avatar'])
                photo.save('AVATAR_NEW_USER_{}_{}'.format(common_models.get_date_stamp_str(), photo.name),
                           custom_bucket=settings.STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'])

                # Process image to save
                payload['avatar'] = photo.compress()
            except TypeError:
                raise ValidationError('Avatar image is not of type image')

        serializer = account_serializers.UserSerializer(data=payload)

        if serializer.is_valid():
            serializer.save()

            response = get_default_response('201')
            response.data = serializer.data
        else:
            response = get_default_response('409')
            response.data['message'] = list()
            response.data['userMessage'] = list()

            # Does email already exist?
            if 'email' in serializer.errors:
                if 'user with this email already exists.' in serializer.errors['email']:
                    response.data['message'].append('Email already exists')
                    response.data['userMessage'].append('A user with the same email already exists. '
                                                        'Did you forget your login?')
                else:
                    raise ValidationError(serializer.errors)

            # Does username already exist?
            if 'username' in serializer.errors:
                if 'user with this username already exists.' in serializer.errors['username']:
                    response.data['message'].append('Username already exists')
                    response.data['userMessage'].append('A user with the same username already exists. '
                                                        'Please choose a different username.')
                else:
                    raise ValidationError(serializer.errors)

            # For all other errors
            if 'email' not in serializer.errors and 'username' not in serializer.errors:
                raise ValidationError(serializer.errors)

        return response
