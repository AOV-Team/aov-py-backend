from apps.account import models as account_models
from apps.common import models as common_models
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

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=512)
    instagram_handle = models.CharField(max_length=128)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    brand = models.CharField(max_length=512)
    title = models.CharField(max_length=512)
    description = models.TextField()
    photos = "" # Another potential FK
    price = models.DecimalField(max_digits=8, decimal_places=2)
    paypal_email = models.URLField(max_length=2083)