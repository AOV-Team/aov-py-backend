from apps.podcast.models import Camera, GetFeaturedRequest, Requester
from django.conf import settings
from django.contrib import admin


class RequesterAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "location", "instagram_handle")
    search_fields = ("email", "full_name", "instagram_handle")

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG or (request.user and (request.user.is_superuser or request.user.is_staff)):
            return True

        return False


class GetFeaturedRequestAdmin(admin.ModelAdmin):
    list_display = ("image", "reviewed", "requester_fk")
    readonly_fields = ("requester_fk",)
    search_fields = ("requester_fk__email", "requester_fk__instagram_handle",
                     "requester_fk__full_name")
    list_filter = ("reviewed",)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG or (request.user and (request.user.is_superuser or request.user.is_staff)):
            return True

        return False


class CameraAdmin(admin.ModelAdmin):
    list_display = ("model", "get_featured_request_fk")
    readonly_fields = ("get_featured_request_fk",)
    search_fields = ("model",)
    ordering = ("model",)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG or (request.user and (request.user.is_superuser or request.user.is_staff)):
            return True

        return False


admin.site.register(Camera, CameraAdmin)
admin.site.register(GetFeaturedRequest, GetFeaturedRequestAdmin)
admin.site.register(Requester, RequesterAdmin)
