from apps.account import models as account_models
from apps.common import models as common_models
from apps.photo import models as photo_models
from django.db import models


class MarketplaceUser(account_models.User):
    class Meta:
        proxy = True
        verbose_name_plural = "Marketplace Users"


class Listing(common_models.EditMixin):
    CATEGORY_CHOICES = (
        ('Camera', 'Camera'),
        ('Lens', 'Lens'),
        ('Camera Bag', 'Camera Bag'),
        ('Other Accessory', 'Other Accessory')
    )

    owner = models.ForeignKey(account_models.User)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    brand = models.CharField(max_length=512)
    title = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)
    photos = models.ManyToManyField(photo_models.Photo, symmetrical=False, related_name="listing_photos")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    paypal_email = models.URLField(max_length=2083)

    class Meta:
        verbose_name_plural = "Listings"


class OfferManager(models.Manager):
    """
        Manager class for the Offer model to allow for updating of the offer
    """

    def create_or_update(self, **kwargs):
        new_offer = Offer(**kwargs)
        existing = Offer.objects.filter(listing=new_offer.listing, owner=new_offer.owner, buyer=new_offer.buyer).first()

        if existing:
            new_offer.pk = existing.pk
            new_offer.id = existing.id
            new_offer.created_at = existing.created_at
        new_offer.save()
        return new_offer


class Offer(common_models.EditMixin):
    STATUS_CHOICES = (
        ('O', 'Open'),
        ('A', 'Accepted'),
        ('R', 'Rescinded'),
        ('D', 'Denied')
    )

    listing = models.ForeignKey(Listing) # FK to Gear model
    owner = models.ForeignKey(account_models.User, related_name="owner")
    buyer = models.ForeignKey(account_models.User, related_name="buyer")
    offer_value = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')

    objects = OfferManager()

    class Meta:
        verbose_name_plural = "Offers"