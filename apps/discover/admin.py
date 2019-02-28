from apps.common.models import get_date_stamp_str
from apps.discover import models as discover_models
from django.conf import settings
from django.contrib import admin


class DownloaderAdmin(admin.ModelAdmin):
    """
    Admin class for the Downloader object
    """
    actions = ['download_csv']
    list_display = ("email", "name", "location")
    search_fields = ("email", "name", "location", "state_sponsor__name",)


    def download_csv(self, request, queryset):
        """
        Action to download a queryset of Downloaders into a CSV
        :return:
        """
        import csv
        from django.http import HttpResponse
        from io import StringIO

        queryset = queryset.exclude(email__icontains="test").exclude(email__icontains="Anonymous")
        f = StringIO()
        writer = csv.writer(f)

        writer.writerow(["Name", "Email", "Location", "Sponsor", "State"])

        for name, email, location, sponsor, state in queryset.values_list(
                'name', 'email', 'location', 'state_sponsor__sponsor__name', 'state_sponsor__state__name'):
            writer.writerow([name, email, location, sponsor, state])

        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=downloaders-{}.csv'.format(get_date_stamp_str())

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG or (request.user and (request.user.is_superuser or request.user.is_staff)):
            return True

        return False


class StateAdmin(admin.ModelAdmin):
    """
    Admin class for the State model
    """
    list_display = ("name", "icon", "display")
    search_fields = ("name",)

    def has_delete_permission(self, request, obj=None):
        # No one can delete these objects, only edit them.
        return False


class SponsorAdmin(admin.ModelAdmin):
    """
    Admin class for the Sponsor model
    """
    list_display = ("name", "social_handle", "website", "profile_image")
    search_fields = ("name", "social_handle", "website")

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG or (request.user and (request.user.is_superuser or request.user.is_staff)):
            return True

        return False

admin.site.register(discover_models.Downloader, DownloaderAdmin)
admin.site.register(discover_models.State, StateAdmin)
