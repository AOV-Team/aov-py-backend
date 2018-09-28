from apps.account import models as account_models
from apps.account import password
from apps.account import serializers as account_serializers
from apps.account import tasks as account_tasks
from apps.common import models as common_models
from apps.common.mailer import send_transactional_email
from apps.common.exceptions import ForbiddenValue, OverLimitException
from apps.common.serializers import setup_eager_loading
from apps.common.views import get_default_response, DefaultResultsSetPagination, LargeResultsSetPagination, \
    MediumResultsSetPagination, remove_pks_from_payload
from apps.communication.models import PushNotificationRecord
from apps.communication.tasks import send_push_notification
from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from apps.photo.photo import Photo
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Polygon
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.shortcuts import render
from django.utils import timezone
from json.decoder import JSONDecodeError
from push_notifications.apns import APNSServerError
from push_notifications.models import APNSDevice
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.views import APIView
from rest_framework_tracking.mixins import LoggingMixin
from social.apps.django_app.utils import load_strategy
from social.apps.django_app.utils import load_backend
from social.exceptions import AuthAlreadyAssociated
from urllib.parse import quote_plus
import json



class AuthenticateViewSet(APIView):
    """
    /api/auth
    """
    permission_classes = (permissions.AllowAny,)
    queryset = account_models.User.objects.all()

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


class BlockUserViewSet(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MediumResultsSetPagination
    serializer_class = account_serializers.UserPublicSerializer

    def get_queryset(self):
        """
            Return a list of Blocked users

        :return: Queryset of Blocked Users for a given User
        """


        accessing_user = TokenAuthentication().authenticate(self.request)[0]
        blocking_user_pk = self.kwargs.get("pk")
        blocking_user = account_models.User.objects.filter(id=blocking_user_pk)
        blocked_users = account_models.User.objects.none()

        if blocking_user.exists() and accessing_user.id == int(blocking_user_pk):
            blocked_user_entries = account_models.Blocked.objects.filter(blocked_by=blocking_user)
            blocked_users = account_models.User.objects.filter(
                id__in=blocked_user_entries.values_list("user", flat=True))

        return blocked_users

    def post(self, request, **kwargs):
        """
            Create a new Blocked entry for accessing user

        :param request: HTTP Request object that contains the id of the offending user
        :param kwargs: Additional keyword arguments provided via the url, in this case the PK for the blocking User
        :return: HTTP Response verifying the block was successful
        """

        blocking_user_pk = kwargs.get("pk")
        blocking_user = account_models.User.objects.filter(id=blocking_user_pk)
        user_getting_blocked = request.data.get("user_id")
        remove_block = request.data.get("remove")
        response = get_default_response('200')

        if blocking_user.exists():
            # Check if the user the block is for is already blocked by the blocking user
            blocking_user = blocking_user.first()

            # If this is a request to remove the block, process that
            if remove_block:
                blocked_entry = account_models.Blocked.objects.filter(
                    user_id=user_getting_blocked, blocked_by=blocking_user)
                blocked_entry.delete()
                return response

            blocked_ids = account_models.Blocked.objects.filter(blocked_by=blocking_user).values_list("user", flat=True)

            if user_getting_blocked not in blocked_ids:
                new_block = account_models.Blocked.objects.create(user_id=user_getting_blocked, blocked_by=blocking_user)

                serialized = account_serializers.BlockedSerializer(new_block).data
                response.data = serialized

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
        # Adorama base link
        base_gear_url = "https://www.adorama.com/l/?kbid=913826&searchinfo="
        # Amazon base link
        # base_gear_url = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="

        if 'item_make' in payload and 'item_model' in payload:
            # Only admins can add links or set reviewed=True
            if ('link' in payload or 'reviewed' in payload) and not authenticated_user.is_admin:
                raise PermissionDenied('You must be an admin to set "link" or "reviewed"')

            if ('link' not in payload) and not authenticated_user.is_admin:
                # Generate the search link to use
                payload["link"] = base_gear_url + quote_plus(payload["item_make"] + " " + payload["item_model"])

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


# class MeViewSet(generics.RetrieveAPIView, generics.UpdateAPIView):
class MeViewSet(generics.GenericAPIView):
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

        # Add the last_login update here, as the middleware ignores it, or this endpoint fails to update the object
        payload.update({"last_login": timezone.now()})

        user = account_models.User.objects.filter(email__iexact=authenticated_user.email).first()

        # If user wants to change their username, ensure that no other user has it already
        if 'username' in payload:
            already_existing = account_models.User.objects.filter(
                username=payload['username']).exclude(id=authenticated_user.id).exists()

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

        # updated_user = account_models.User.objects.get(id=authenticated_user.id)

        # Password
        if 'password' in payload:
            if 'existing_password' in payload:
                # We have to do this manually due to case insensitive email
                existing = False

                if user and user.check_password(payload['existing_password']):
                    existing = True

                if existing:
                    user.set_password(payload['password'])
                    del payload['existing_password']
                else:
                    raise PermissionDenied('Old password is not correct')
            else:
                raise ValidationError('Existing password is required')

            # We don't want this in the next step
            del payload['password']

        # Update user
        for item in payload:
            setattr(user, item, payload[item])
        user.save()

        serializer = account_serializers.UserSerializer(user)
        response.data = serializer.data

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


class MeProfileViewSet(generics.GenericAPIView):
    """
    api/me/profile
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.Profile.objects.all()
    serializer_class = account_serializers.ProfileSerializer

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
        profile = account_models.Profile.objects.filter(user=authenticated_user).first()
        if not profile:
            response.data['message'] = 'Profile does not exist.'
            response.data['userMessage'] = 'You do not have a profile.'
            return response

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

        serializer = account_serializers.ProfileSerializer(profile, data=payload, partial=True)

        if serializer.is_valid():
            serializer.save()

            response = get_default_response('200')
            response.data = serializer.data
        else:
            response = get_default_response('400')
            response['message'] = serializer.errors

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

                    # Send a push notification to the followed user
                    followed_device = APNSDevice.objects.filter(user=user)
                    message = "{} started following you, {}.".format(auth_user.username, user.username)

                    # This check is here to make sure the record is only created for devices that we have. No APNS means no
                    # permission for notifications on the device.
                    if followed_device.exists():
                        # To ensure we have the most recent APNSDevice entry, get a QuerySet of only the first item
                        followed_device = APNSDevice.objects.filter(id=followed_device.first().id)

                        try:
                            send_push_notification(message, followed_device.values_list("id", flat=True))

                            # Add history of the notification.
                            PushNotificationRecord.objects.create(message=message, receiver=followed_device.first(), action="F",
                                                                  content_object=user, sender=auth_user)
                        except APNSServerError:
                            pass

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


class UserLocationViewSet(generics.ListCreateAPIView):
    """
        /api/users/{}/location
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = account_serializers.UserLocationSerializer

    def get_queryset(self):
        """
            Retrieval method

            :return: QuerySet
            """
        user_id = self.kwargs.get('user_id', None)
        geo_location = self.request.query_params.get('geo_location')
        query_params = {
            "user_id": user_id
        }

        # If searching by a box of coordinates
        # Format ?geo_location=SW LONG,SW LAT,NE LONG, NE LAT
        if geo_location:
            coordinates = tuple(geo_location.split(','))

            # Check that we have 4 coordinates
            # And each coordinate needs to be a number
            if len(coordinates) != 4:
                raise ValidationError('Expecting geo_location to have 4 coordinates: "SW LONG,SW LAT,NE LONG, NE LAT"')
            else:
                try:
                    for c in coordinates:
                        float(c)
                except ValueError:
                    raise ValidationError('Expecting number format for coordinates')

            rectangle = Polygon.from_bbox(coordinates)
            query_params['coordinates__contained'] = rectangle
            del query_params["user_id"]

        user_location = account_models.UserLocation.objects.filter(**query_params)
        return user_location

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

        data = self.request.query_params.get("data", None)
        if data:
            if data == "renders":
                self.serializer_class = photo_serializers.PhotoRenderSerializer

            elif data == "details":
                self.serializer_class = photo_serializers.PhotoDetailsSerializer

            else:
                self.serializer_class = photo_serializers.PhotoSerializer

        photos = photo_models.Photo.objects.filter(user=user, public=True).order_by('-id')
        paginated_photos = self.paginate_queryset(photos)

        serialized_items = list()

        for photo in paginated_photos:
            serialized_items.append(self.serializer_class(photo, context={"request": request}).data)

        response = self.get_paginated_response(serialized_items)

        return response


class LoggedUserPhotosViewSet(LoggingMixin, UserPhotosViewSet):
    logging_methods = ['GET']

    def should_log(self, request, response):
        if not request.method in self.logging_methods:
            return False
        return response.status_code == 200


@staff_member_required
def power_users_admin(request):
    """
    Advanced power user stats

    :param request: Request object
    :return: render()
    """

    date = request.GET.get("date")

    # Power Users
    users = account_models.User.objects.filter(is_active=True, age__isnull=False, age__gte=1)
    sessions = account_models.UserSession.objects.none()
    start = None
    end = None
    if date:
        dates = date.split(' - ')

        if len(dates) == 2:
            start = datetime.strptime(dates[0], '%Y-%m-%d')
            end = datetime.strptime(dates[1], '%Y-%m-%d') + timedelta(days=1)

            sessions = sessions | account_models.UserSession.objects.filter(
                user__in=users, modified_at__gte=start, modified_at__lte=end)

    else:
        cutoff = datetime.now() - timedelta(days=7)
        sessions = sessions | account_models.UserSession.objects.filter(user__in=users, modified_at__gte=cutoff)

    power_users = account_models.User.objects.filter(id__in=sessions.values_list("user", flat=True))
    power_users_display = power_users.annotate(
        Count("usersession", distinct=True)).filter(usersession__count__gte=3)
    power_users_display = power_users_display.order_by("-usersession__count")

    # Set up the query object for action types
    if start and end:
        filter_options = {
            "created_at__gte": start,
            "created_at__lte": end,
            "user": None
        }
    else:
        filter_options = {
            "user": None
        }

    for user in power_users_display:
        filter_options.update({"user": user})
        user.photo__count = photo_models.Photo.objects.filter(**filter_options).count()
        user.photovote__count = photo_models.PhotoVote.objects.filter(**filter_options).count()
        user.photocomment__count = photo_models.PhotoComment.objects.filter(**filter_options).count()
        user.total_actions = user.photocomment__count + user.photovote__count + user.photo__count

    count = power_users_display.count()
    power_users_display = list(sorted(power_users_display, key=lambda user: user.total_actions))

    # Pagination
    paginator = Paginator(power_users_display, 30)
    page = request.GET.get('page')

    try:
        power_users_display = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        power_users_display = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        power_users_display = paginator.page(paginator.num_pages)

    # Ensure we retain query string even when paginating
    get_copy = request.GET.copy()
    parameters = get_copy.pop('page', True) and get_copy.urlencode()

    context = {
        'parameters': parameters,
        'users': power_users_display,
        'users_count': count
    }

    return render(request, 'power_users.html', context)


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
        user = account_models.User.objects.filter(id=kwargs.get('pk'))
        profile = account_models.Profile.objects.filter(user=user).first()

        if profile and user:
            response = get_default_response('200')
            response.data = account_serializers.ProfileSerializer(profile).data

        else:
            response = get_default_response('404')
            response.data['message'] = 'User does not exist.'
            response.data['userMessage'] = 'User does not exist.'

        return response


class UserSearchViewSet(generics.ListAPIView):
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
            qs = self.queryset.filter(Q(username__icontains=keywords) | Q(social_name__icontains=keywords) |
                                      Q(first_name__icontains=keywords) | Q(last_name__icontains=keywords))

        return qs.order_by("username")


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


class UserStarredPhotosViewSet(generics.ListAPIView):
    """
        API view to retrieve the photos starred by the accessing user

    """
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = DefaultResultsSetPagination
    serializer_class = photo_serializers.PhotoSerializer

    def get_queryset(self):
        """
            Method to retrieve the queryset of appropriate photos

        :return: QuerySet of photos
        """

        auth_user = TokenAuthentication().authenticate(self.request)[0]
        stars = account_models.UserInterest.objects.filter(interest_type="star", user=auth_user)

        return photo_models.Photo.objects.filter(id__in=stars.values_list("object_id", flat=True).distinct("object_id"))


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


class SampleLoginViewSet(generics.GenericAPIView):
    queryset = account_models.User.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, **kwargs):
        user = account_models.User.objects.get(id=kwargs.get("user_id"))
        return get_default_response('200')
