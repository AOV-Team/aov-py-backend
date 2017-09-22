from apps.account.serializers import UserPublicSerializer
from apps.marketplace import models
from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from rest_framework import serializers


class ListingSerializer(serializers.ModelSerializer):
    owner = UserPublicSerializer
    photos = photo_serializers.PhotoSerializer

    class Meta:
        model = models.Listing
        fields = ('id', 'owner', 'category', 'brand', 'title', 'description', 'price', 'paypal_email')


class OfferSerializer(serializers.ModelSerializer):
    listing = ListingSerializer()
    owner = UserPublicSerializer()
    buyer = UserPublicSerializer()

    class Meta:
        model = models.Offer
        fields = ('id', 'listing', 'owner', 'buyer', 'offer_value', 'status')