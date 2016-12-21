from apps.account import models as account_models
from apps.account import password
from apps.account import serializers as account_serializers
from apps.account import tasks as account_tasks
from apps.common import models as common_models
from apps.common.mailer import send_transactional_email
from apps.common.exceptions import ForbiddenValue, OverLimitException
from apps.common.views import get_default_response, remove_pks_from_payload
from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from apps.photo.photo import Photo
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from json.decoder import JSONDecodeError
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied, ValidationError
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
            # TODO remove this a few weeks after transition to Django backend
            # This is for smoothly transitioning users to the new backend
            try:
                if 'set' in payload and 'auth' in payload:
                    if payload['set'] and payload['auth'] == 'okgo':
                        user = account_models.User.objects.get(email=payload['email'])

                        if not user.password:
                            user.set_password(payload['password'])
                            user.save()
            except ObjectDoesNotExist:
                response = get_default_response('401')
                response.data['message'] = 'Authentication failed'
                response.data['userMessage'] = 'Email or password incorrect. Please try again.'
                return response
            # END TODO

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
                    user = account_models.User.objects.get(email=saved_email, is_active=True)
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
                user = account_models.User.objects.get(email=payload['email'])
                code = password.create_password_reset_code(user)

                # Send email to user
                send_transactional_email(user, 'password-reset-code', password_reset_code=code)
            except ObjectDoesNotExist:
                pass

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
        # Explicitedly converting to dict just in case...
        payload = dict(remove_pks_from_payload('user', payload))

        if 'email' in payload:
            del payload['email']

        if 'is_active' in payload:
            del payload['is_active']

        if 'is_admin' in payload:
            del payload['is_admin']

        if 'is_superuser' in payload:
            del payload['is_superuser']

        if 'username' in payload:
            del payload['username']

        updated_user = account_models.User.objects.get(id=authenticated_user.id)

        # Password
        if 'password' in payload:
            if 'existing_password' in payload:
                existing = authenticate(email=authenticated_user.email, password=payload['existing_password'])

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
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
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
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user

        photos = photo_models.Photo.objects.filter(user=authenticated_user, public=True).order_by('-id')
        paginated_photos = self.paginate_queryset(photos)

        serialized_items = list()

        for photo in paginated_photos:
            serialized_items.append(photo_serializers.PhotoSerializer(photo).data)

        response = self.get_paginated_response(serialized_items)

        return response


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
        response = get_default_response('200')

        try:
            user = account_models.User.objects.get(id=kwargs.get('pk'), is_active=True)

            response.data = account_serializers.UserPublicSerializer(user).data
        except ObjectDoesNotExist:
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
