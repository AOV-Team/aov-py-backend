from apps.account import authenticate
from apps.account import models as account_models
from apps.account import serializers as account_serializers
from apps.common.mailer import send_transactional_email
from apps.common.views import get_default_response
from django.contrib.auth.hashers import make_password
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError


class MarketplaceActivationViewSet(generics.GenericAPIView):
    """
        Endpoint for a user to activate their marketplace account.

    """
    permission_classes = (permissions.AllowAny,)
    queryset = account_models.User.objects.all()

    @staticmethod
    def post(request):
        """
            Sets the is_active field to True for the associated user

        :return: Response object
        """
        payload = request.data

        if 'code' in payload:
            code = payload['code']
            email = authenticate.get_authenticating_email(code)
            user = account_models.User.objects.filter(email=email)

            if user.exists():
                user.update(is_active=True)
                authenticate.delete_authentication_code(code)
                response = get_default_response('200')
                response.data['message'] = "User activated successfully."
                response.data['userMessage'] = "You've successfully verified your email!"

                return response

        else:
            response = get_default_response('400')
            return response


class MarketplaceUserViewSet(generics.CreateAPIView):
    """
    /api/users

    Endpoint class for User model, specifically being created on the Marketplace
    http://stackoverflow.com/questions/27468552/changing-serializer-fields-on-the-fly/#answer-27471503
    """
    permission_classes = (permissions.AllowAny,)
    queryset = account_models.User.objects.all()
    serializer_class = account_serializers.UserSerializer

    def post(self, request, *args, **kwargs):
        """
        Create a new user

        :param request: Request object
        :return: Response object
        """
        # .copy() fixes 500 error when content type is
        # application/x-www-form-urlencoded;
        payload = request.data.copy()

        # Make all emails lowercase
        if 'email' in payload:
            payload['email'] = payload['email'].lower()

        # Set is_active to false, pending verification
        payload['is_active'] = False

        # Set the signup_source field for use in the admin
        payload['signup_source'] = "MK"

        serializer = account_serializers.UserSerializer(data=payload)

        if serializer.is_valid():
            if 'password' in payload:
                serializer.save(password=make_password(payload['password']))
            else:
                raise ValidationError('Password is required')

            # Set a uuid value in redis that will be used for activation
            user = account_models.User.objects.filter(email=payload['email']).first()
            code = authenticate.create_authentication_code(user)

            # Send email to user
            send_transactional_email(user, 'user-authentication-email', authentication_code=code)

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
