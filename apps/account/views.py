from apps.account import models as account_models
from apps.account import password
from apps.account import serializers as account_serializers
from apps.account import tasks as account_tasks
from apps.common import models as common_models
from apps.common.mailer import send_transactional_email
from apps.common.exceptions import ForbiddenValue, OverLimitException
from apps.common.serializers import setup_eager_loading
from apps.common.views import get_default_response, LargeResultsSetPagination, MediumResultsSetPagination, \
    remove_pks_from_payload
from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from apps.photo.photo import Photo
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import TrigramSimilarity, SearchQuery, SearchVector, SearchRank
from django.core.exceptions import ObjectDoesNotExist
from json.decoder import JSONDecodeError
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.views import APIView
from social.apps.django_app.utils import load_strategy
from social.apps.django_app.utils import load_backend
from social.exceptions import AuthAlreadyAssociated
import json


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
            response.data['userMessage'] = 'Cannot log you out - you are not logged in!'

        return response

    def post(self, request):
        """
        Log a user in
        :param request: Request object
        :return: Response object
        """
        raw_payload = request.body
        payload = request.data
        email = payload.get('email')
        password = payload.get('password')
        response = get_default_response('400')
        content_type = request.META['CONTENT_TYPE']

        # This is to handle app versions that don't use application/json
        if content_type == 'application/x-www-form-urlencoded' and email is None and password is None:
            new_payload = json.loads(raw_payload.decode('utf-8'))
            email = new_payload['email']
            password = new_payload['password']

        if email and password:
            # TODO remove this a few weeks after transition to Django backend
            # This is for smoothly transitioning users to the new backend
            try:
                if 'set' in payload and 'auth' in payload:
                    if payload['set'] and payload['auth'] == 'okgo':
                        user = account_models.User.objects.get(email=payload['email'].lower())

                        if not user.password:
                            user.set_password(payload['password'])
                            user.save()
            except ObjectDoesNotExist:
                response = get_default_response('401')
                response.data['message'] = 'Authentication failed'
                response.data['userMessage'] = 'Email or password incorrect. Please try again.'
                return response
            # END TODO

            try:
                # Have to do this manually since authenticate does not support case insensitive email
                user_model = get_user_model()
                user = user_model.objects.filter(email__iexact=email).first()

                if not user or not user.check_password(password):
                    # This is not the actual exception but we want it handled the same as if the user was not found
                    raise ObjectDoesNotExist

                if user.is_active:
                    token = Token.objects.get_or_create(user=user)
                    response = get_default_response('201')
                    response.data['token'] = token[0].key
                else:
                    response = get_default_response('403')
                    response.data['message'] = 'User inactive'
                    response.data['userMessage'] = 'Cannot log you in because your user is inactive'
            except ObjectDoesNotExist:
                response = get_default_response('401')
                response.data['message'] = 'Authentication failed'
                response.data['userMessage'] = 'Email or password incorrect. Please try again.'

        return response


class AuthenticateResetViewSet(APIView):
    permission_classes = (permissions.AllowAny,)

    def patch(self, request, **kwargs):
        """
        Update password

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        response = get_default_response('400')
        payload = request.data

        if 'code' in payload and 'password' in payload:
            try:
                saved_email = password.get_password_reset_email(payload['code'])

                if saved_email:
                    user = account_models.User.objects.get(email__iexact=saved_email, is_active=True)
                    user.set_password(payload['password'])
                    user.save()

                    response = get_default_response('200')
                    response.data['message'] = 'Password updated'
                    response.data['userMessage'] = 'Your password has been updated'
                else:
                    response = get_default_response('403')
                    response.data['message'] = 'Code is not valid'
                    response.data['userMessage'] = 'Your code is not valid'
            except ObjectDoesNotExist:
                response = get_default_response('404')
                response.data['message'] = 'User does not exist'
                response.data['userMessage'] = 'The user does not exist.'

        return response

    def post(self, request, **kwargs):
        """
        Request a code to reset password

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        response = get_default_response('400')
        payload = request.data

        if 'email' in payload:
            response = get_default_response('201')

            try:
                # Create code in Redis
                user = account_models.User.objects.get(email__iexact=payload['email'])
                code = password.create_password_reset_code(user)

                # Send email to user
                send_transactional_email(user, 'password-reset-code', password_reset_code=code)
            except ObjectDoesNotExist:
                pass

        return response


class GearSingleViewSet(generics.RetrieveAPIView, generics.UpdateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MediumResultsSetPagination
    serializer_class = account_serializers.GearSerializer

    def get_queryset(self):
        """
        Return public gear

        :return: QuerySet
        """
        return account_models.Gear.objects.filter(public=True)

    def patch(self, request, **kwargs):
        """
        Update gear

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user
        payload = request.data
        gear_id = kwargs.get('pk', None)
        response = get_default_response('400')

        # Only admins can edit gear
        if not authenticated_user.is_admin:
            response = get_default_response('403')
            response.data['message'] = 'Only admins can edit gear'
            return response

        try:
            # Get existing gear
            gear = account_models.Gear.objects.get(id=gear_id)
            serializer = account_serializers.GearSerializer(data=payload, partial=True)

            if serializer.is_valid():
                serializer.update(gear, serializer.validated_data)

                response = get_default_response('200')
                response.data = account_serializers.GearSerializer(account_models.Gear.objects.get(id=gear_id)).data
            else:
                raise ValidationError(serializer.errors)
        except ObjectDoesNotExist:
            response = get_default_response('404')

        return response


class GearViewSet(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MediumResultsSetPagination
    serializer_class = account_serializers.GearSerializer

    def get_queryset(self):
        """
        Query for gear

        :return: QuerySet
        """
        make = self.request.GET.get('item_make')
        model = self.request.GET.get('item_model')
        queryset = account_models.Gear.objects.filter(public=True)

        if make:
            queryset = queryset.annotate(make_similarity=TrigramSimilarity('item_make', make))\
                .filter(make_similarity__gt=0.2).order_by('-make_similarity')

        if model:
            queryset = account_models.Gear.objects.annotate(model_similarity=TrigramSimilarity('item_model', model))\
                .filter(model_similarity__gt=0.2).order_by('-model_similarity')

        return queryset

    def post(self, request):
        """
        Create a gear entry

        :param request: Request object
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user
        payload = request.data
        response = get_default_response('400')

        if 'item_make' in payload and 'item_model' in payload:
            # Only admins can add links or set reviewed=True
            if ('link' in payload or 'reviewed' in payload) and not authenticated_user.is_admin:
                raise PermissionDenied('You must be an admin to set "link" or "reviewed"')

            # Check if existing
            existing = account_models.Gear.objects\
                .filter(item_make=payload['item_make'], item_model=payload['item_model']).first()

            if existing:
                response = get_default_response('409')
                response.data['message'] = 'Gear already exists. Use PATCH to update.'
                return response

            serializer = account_serializers.GearSerializer(data=payload)

            if serializer.is_valid():
                serializer.save()

                response = get_default_response('201')
                response.data = serializer.data
            else:
                raise ValidationError(serializer.errors)

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

        # If user wants to change their username, ensure that no other user has it already
        if 'username' in payload:
            already_existing = account_models.User.objects.filter(username=payload['username'])\
                .exclude(id=authenticated_user.id)

            if already_existing:
                response = get_default_response('409')
                response.data['message'] = 'Username already exists.'
                response.data['userMessage'] = 'Cannot update your information. Username is taken.'
                return response

        # Avatar
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

        if 'email' in payload:
            del payload['email']

        if 'is_active' in payload:
            del payload['is_active']

        if 'is_admin' in payload:
            del payload['is_admin']

        if 'is_superuser' in payload:
            del payload['is_superuser']

        updated_user = account_models.User.objects.get(id=authenticated_user.id)

        # Password
        if 'password' in payload:
            if 'existing_password' in payload:
                # We have to do this manually due to case insensitive email
                existing = False
                user_model = get_user_model()
                user = user_model.objects\
                    .filter(email__iexact=authenticated_user.email).first()

                if user and user.check_password(payload['existing_password']):
                    existing = True

                if existing:
                    updated_user.set_password(payload['password'])
                    del payload['existing_password']
                else:
                    raise PermissionDenied('Old password is not correct')
            else:
                raise ValidationError('Existing password is required')

            # We don't want this in the next step
            del payload['password']

        # Update user
        for key in payload:
            setattr(updated_user, key, payload[key])

        updated_user.save()

        response.data = account_serializers.UserSerializer(updated_user).data

        return response


class MeGearViewSet(APIView):
    """
    api/me/gear
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.Profile.objects.all()

    def delete(self, request):
        """
        Remove all gear

        :param request: Request object
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        response = get_default_response('200')

        try:
            profile = account_models.Profile.objects.get(user=authenticated_user)
            gear = account_models.Gear(profile)
            gear.save()
        except ObjectDoesNotExist:
            pass

        return response

    def get(self, request, **kwargs):
        """
        Get user's gear

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        response = get_default_response('200')

        try:
            profile = account_models.Profile.objects.get(user=authenticated_user)
            gear = account_models.Gear(profile)

            response.data = gear.all
        except JSONDecodeError:
            response = get_default_response('500')
            response.data['message'] = 'Unable to parse gear data.'
        except ObjectDoesNotExist:
            # If user does not have a profile, return empty list
            response.data = list()

        return response

    def patch(self, request):
        """
        Update gear

        :param request: Request object
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        payload = request.data
        response = get_default_response('400')

        try:
            profile = account_models.Profile.objects.get(user=authenticated_user)
            gear = account_models.Gear(profile, payload)

            if gear.links_valid(payload):
                gear.save()
            else:
                raise ForbiddenValue('Links cannot be updated using this endpoint')

            response = get_default_response('200')
            response.data = gear.all
        except ForbiddenValue as e:
            response = get_default_response('403')
            response.data['message'] = str(e)
        except KeyError as e:
            response.data['message'] = str(e)
        except ObjectDoesNotExist:
            response = get_default_response('403')
            response.data['message'] = 'Profile does not exist. Create a profile for the user to update gear.'
        except OverLimitException as e:
            response.data['message'] = str(e)
        except ValueError as e:
            response.data['message'] = str(e)

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

        # Gear not allowed
        if 'gear' in payload:
            raise ValidationError('Gear not editable. Use /api/me/gear')

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

        existing_profile = account_models.Profile.objects.filter(user=authenticated_user).first()

        # Only create a profile if user doesn't have one
        if not existing_profile:
            # Gear not allowed
            if 'gear' in payload:
                raise ValidationError('Gear not editable. Use /api/me/gear')

            if 'bio' in payload or 'cover_image' in payload:
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
        else:
            response = get_default_response('409')
            response.data['message'] = 'User already has a profile'

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


class UserFollowingViewSet(generics.ListAPIView):
    pagination_class = LargeResultsSetPagination
    permission_classes = (permissions.AllowAny,)
    serializer_class = account_serializers.UserPublicSerializer

    def get_queryset(self):
        """
        Get the users that a user is following

        :return: Queryset
        """
        accessing_user = account_models.User.objects.filter(id=self.kwargs.get('user_id'))

        if accessing_user.exists():
            # Gather the users he is following
            following = account_models.User.objects.filter(follower=accessing_user).order_by('-created_at')
            return following

        else:
            raise NotFound('User does not exist')


class UserFollowersViewSet(generics.ListCreateAPIView):
    pagination_class = LargeResultsSetPagination
    permission_classes = (permissions.AllowAny,)
    serializer_class = account_serializers.UserPublicSerializer

    def get_queryset(self):
        """
        Get followers for a user

        :return: Queryset
        """
        try:
            user = account_models.User.objects.get(id=self.kwargs.get('user_id'))
            return user.follower.all()

        except ObjectDoesNotExist:
            raise NotFound('User does not exist')

    def post(self, request, **kwargs):
        """
        Follow a user

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)

        if authentication:
            auth_user = authentication[0]

            try:
                user = account_models.User.objects.get(id=kwargs.get('user_id'), is_active=True)
                follow = user.follower.filter(id=auth_user.id).first()

                # Create follow entry
                # If user is already following this user, return HTTP 409 status code
                if not follow:
                    user.follower.add(auth_user)
                    user.save()

                    return get_default_response('201')
                else:
                    return get_default_response('409')
            except ObjectDoesNotExist:
                raise NotFound('User does not exist')
        else:
            return get_default_response('401')


class UserFollowerSingleViewSet(generics.DestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, **kwargs):
        """
        Stop following a user

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        auth_user = authentication[0]

        try:
            user = account_models.User.objects.get(id=kwargs.get('user_id'), is_active=True)
            user.follower.remove(auth_user)
            user.save()

            return get_default_response('200')
        except ObjectDoesNotExist:
            raise NotFound('User does not exist')


class UserLocationViewSet(generics.GenericAPIView):
    """
        /api/users/{}/location
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = account_serializers.UserLocationSerializer

    def get(self, request, **kwargs):
        """
        Retrieval method

        :return: QuerySet
        """
        user_id = kwargs.get('user_id', None)

        user = account_models.User.objects.filter(id=user_id)
        user_location = account_models.UserLocation.objects.filter(user=user)

        if user_location.exists():
            serialized_data = account_serializers.UserLocationSerializer(user_location.first())

            response = get_default_response('200')
            response.data = serialized_data.data
            return response
        else:
            raise NotFound('UserLocation does not exist')

    def post(self, request, **kwargs):
        """

        :param request: HTTP Request object containing data necessary to create the database entry
        :param kwargs: Additional keyword arguments passed via url. This endpoint expects a user id
        :return: HTTP response object confirming or denying execution of the request
        """

        authentication = TokenAuthentication().authenticate(request)
        auth_user = authentication[0]
        payload = request.data
        user_id = kwargs.get('user_id', None)

        if auth_user.id != int(user_id):
            return get_default_response('403')

        payload['user'] = user_id
        serializer = account_serializers.UserLocationSerializer(data=payload)

        if serializer.is_valid():
            serializer.save()

            response = get_default_response('200')
            response.data = serializer.data
        else:
            raise ValidationError(serializer.errors)

        return response


class UserPhotosViewSet(generics.ListAPIView):
    """
    /api/users/{}/photos
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    @setup_eager_loading
    def get_queryset(self):
        return photo_models.Photo.objects.all()

    def get(self, request, **kwargs):
        """
        Get user's photos

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        try:
            user = account_models.User.objects.get(id=kwargs.get('user_id'))
        except ObjectDoesNotExist:
            raise NotFound('User does not exist')

        photos = photo_models.Photo.objects.filter(user=user, public=True).order_by('-id')
        paginated_photos = self.paginate_queryset(photos)

        serialized_items = list()

        for photo in paginated_photos:
            serialized_items.append(photo_serializers.PhotoSerializer(photo, context={"request": request}).data)

        response = self.get_paginated_response(serialized_items)

        return response


class UserProfileViewSet(generics.RetrieveAPIView):
    """ /api/users/{}/profile """
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.Profile.objects.all()
    serializer_class = account_serializers.ProfileSerializer

    def get(self, request, **kwargs):
        """
        Get a user's profile

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        try:
            user = account_models.User.objects.get(id=kwargs.get('pk'))
            profile = account_models.Profile.objects.get(user=user)

            response = get_default_response('200')
            response.data = account_serializers.ProfileSerializer(profile).data
            return response
        except ObjectDoesNotExist:
            raise NotFound('User does not exist')


class UserSearchViewSet(generics.RetrieveAPIView):
    """
        /api/users/search

        Endpoint to allow searching for a user by name, username, or social_name

        Search weight priority: First Name, Last Name, Username, Social Name
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.User.objects.all()
    serializer_class = account_serializers.UserPublicSerializer

    def get_queryset(self):
        """
            GET method to return Users based on query values

        :param request: HTTP request object with the query parameters
        :param kwargs: Additional keyword arguments
        :return:
        """
        query_params = self.request.query_params
        keywords = query_params.get("q", None)
        qs = account_models.User.objects.none()
        if keywords:
            query = SearchQuery(keywords)

            # Set up the Vectors with appropriate weights
            first_name_vector = SearchVector("first_name", weight="A")
            last_name_vector = SearchVector("last_name", weight="B")
            username_vector = SearchVector("username", weight="C")
            social_name_vector = SearchVector("social_name", weight="D")

            vectors = first_name_vector + last_name_vector + username_vector + social_name_vector

            qs = self.queryset.annotate(search=vectors).filter(search=query)
            qs = qs.annotate(rank=SearchRank(vectors, query)).order_by("-rank")

        return qs


class UserSingleViewSet(generics.RetrieveAPIView):
    """
    /api/users/{}

    """
    permission_classes = (permissions.AllowAny,)
    queryset = account_models.User.objects.all()
    serializer_class = account_serializers.UserPublicSerializer

    def get(self, request, **kwargs):
        """
        GET a user's public info

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        user_id = kwargs.get('pk', None)
        response = get_default_response('200')

        user = account_models.User.objects.filter(id=user_id, is_active=True)
        # Check for query parameters
        query_params = request.query_params
        query_dict = {
            'id': user_id,
            'is_active': True,
        }
        if 'username' in query_params:
            query_dict['username'] = query_params.get('username')

        user = user.filter(**query_dict)

        if user.exists():
            user = user.first()

            response.data = account_serializers.UserPublicSerializer(user).data
        else:
            response = get_default_response('404')
            response.data['message'] = 'User does not exist.'
            response.data['userMessage'] = 'User does not exist.'

        return response


class UserSingleStarsViewSet(generics.CreateAPIView, generics.RetrieveDestroyAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.User.objects.all()
    serializer_class = account_serializers.UserSerializer

    def delete(self, request, **kwargs):
        """
        Delete a star

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user
        response = get_default_response('200')
        starred_user_id = kwargs.get('pk')

        try:
            try:
                user = account_models.User.objects.get(id=starred_user_id)
            except ObjectDoesNotExist:
                response = get_default_response('404')
                response.data['message'] = 'User does not exist'
                return response

            user_type = ContentType.objects.get_for_model(user)
            interest = account_models.UserInterest.objects.filter(user=authenticated_user, interest_type='star',
                                                                  content_type__pk=user_type.id, object_id=user.id)

            interest.delete()
        except ObjectDoesNotExist:
            # Return 200 even if user wasn't starred
            pass

        return response

    def post(self, request, **kwargs):
        """
        Star a user

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user
        response = get_default_response('400')
        star_user_id = kwargs.get('pk')

        try:
            star_user = account_models.User.objects.get(id=star_user_id)

            # Make sure there is no existing entry
            user_type = ContentType.objects.get_for_model(star_user)
            interest = account_models.UserInterest.objects\
                .filter(user=authenticated_user, interest_type='star', content_type__pk=user_type.id,
                        object_id=star_user.id)\
                .first()

            if not interest:
                account_models.UserInterest.objects.create(content_object=star_user,
                                                           user=authenticated_user, interest_type='star')
                response = get_default_response('201')
            else:
                response = get_default_response('409')
        except ObjectDoesNotExist:
            response = get_default_response('404')
            response.data['message'] = 'User you attempted to star does not exist'

        return response


class UserViewSet(generics.CreateAPIView):
    """
    /api/users

    Endpoint class for User model
    http://stackoverflow.com/questions/27468552/changing-serializer-fields-on-the-fly/#answer-27471503
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
        # .copy() fixes 500 error when content type is
        # application/x-www-form-urlencoded;
        payload = request.data.copy()
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

        # Make all emails lowercase
        if 'email' in payload:
            payload['email'] = payload['email'].lower()

        serializer = account_serializers.UserSerializer(data=payload)

        if serializer.is_valid():
            if 'password' in payload:
                serializer.save(password=make_password(payload['password']))
            else:
                raise ValidationError('Password is required')

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
