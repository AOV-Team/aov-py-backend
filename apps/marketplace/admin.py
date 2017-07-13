from apps.account import admin as account_admin
from apps.account import models as account_models
from apps.marketplace import models as marketplace_models
from django.contrib import admin
from django.db.models import Count


class MarketplaceUserAdmin(admin.ModelAdmin):
    """
        Custom admin to only return users that signed up using the Marketplace

    """
    def get_queryset(self, request):
        qs = super(MarketplaceUserAdmin, self).get_queryset(request).annotate(Count('photo')).annotate(Count('follower'))
        return qs.filter(signup_source='MK')

admin.site.register(marketplace_models.MarketplaceUser, MarketplaceUserAdmin)
