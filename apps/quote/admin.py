from apps.quote import models as quote_models
from django.conf import settings
from django.contrib import admin



class QuoteAdmin(admin.ModelAdmin):
    """
    Admin class for the Quote object
    """
    list_display = ("author", "display_date")
    search_fields = ("author", "quote", "display_date")
    ordering = ("-display_date",)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG or (request.user and (request.user.is_superuser or request.user.is_staff)):
            return True

        return False


class QuoteSubscriberAdmin(admin.ModelAdmin):
    """
    Admin class for the QuoteSubscriber model
    """
    list_display = ("email",)
    search_fields = ("email",)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG or (request.user and (request.user.is_superuser or request.user.is_staff)):
            return True

        return False

admin.site.register(quote_models.Quote, QuoteAdmin)
admin.site.register(quote_models.QuoteSubscriber, QuoteSubscriberAdmin)
