from apps.account import authenticate
from apps.account import models as account_models
from apps.account import serializers as account_serializers
from apps.common.mailer import send_transactional_email
from apps.common.views import get_default_response
from apps.marketplace import models as marketplace_models
from apps.marketplace import serializers as marketplace_serializers
from django.contrib.auth.hashers import make_password
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView


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


class MarketplaceListingViewSet(APIView):
    """
        API view set to handle Marketplace offers
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class MarketplaceOfferViewSet(APIView):
    """
        API view set to handle Marketplace offers
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, **kwargs):
        """
            POST method to create MarketplaceOffer object

        :param request: HTTP request object
        :param kwargs: Additional keyword arguments from the url
        :return: HTTP response object
        """

        # Create a new Offer object
        # Send email to owner notifying of offer
        # Return 200 containing information about the offer to the Buyer

        auth_user = TokenAuthentication().authenticate(request)[0]

        payload = request.data
        owner_id = payload.get('owner', None)
        offer_amount = payload.get('amount', None)
        listing_item = payload.get('listing_id', None)

        owner = account_models.User.objects.filter(id=owner_id)

        if owner.exists():
            offer = marketplace_models.Offer.objects.create_or_update(owner_id=owner_id, buyer_id=auth_user.id,
                                                                      offer_value=offer_amount,
                                                                      listing_id=listing_item)

            template_data = {
                'buyer': offer.buyer.email,
                'offer_value': offer.offer_value,
                'listing_title': offer.listing.title
            }

            # Send the email to the owner, notifying them of the offer
            send_transactional_email(owner.first(), 'marketplace-make-offer', **template_data)

            serialized_offer = marketplace_serializers.OfferSerializer(offer).data

            response = get_default_response('201')
            response.data = serialized_offer
            return response

        else:
            response = get_default_response('404')
            return response

    def get(self, request, **kwargs):
        """
            API Endpoint to retrieve current offers for a given user

        :param request: HTTP request object
        :param kwargs: Additional keyword arguments provided via url
        :return: HTTP response object
        """

        user_id = kwargs.get('pk', None)

        user = account_models.User.objects.filter(id=user_id)

        if user.exists():
            # Gather offers for which they are the buyer
            buyer_offers = marketplace_models.Offer.objects.filter(buyer=user)

            # Gather offers for which they are the owner
            owner_offers = marketplace_models.Offer.objects.filter(owner=user)

            serialized_buyer_offers = marketplace_serializers.OfferSerializer(buyer_offers, many=True).data
            serialized_owner_offers = marketplace_serializers.OfferSerializer(owner_offers, many=True).data

            response_data = {
                'buyer': serialized_buyer_offers,
                'owner': serialized_owner_offers
            }

            response = get_default_response('200')
            response.data = response_data

            return response

        else:
            response = get_default_response('404')
            return response
