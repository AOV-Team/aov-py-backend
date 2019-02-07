from apps.podcast import models as podcast_models
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
    list_display = ("requester_fk", "image", "reviewed")
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


class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("title", "episode_number", "participant_social", "published_date", "archived")
    search_fields = ("title", "episode_number", "participant_social", "quote", "description")
    ordering = ("-archived", "episode_number")

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG or (request.user and (request.user.is_superuser or request.user.is_staff)):
            return True

        return False


class PodcastImageAdmin(admin.ModelAdmin):
    list_display = ("image", "episode", "display_type")
    search_fields = ("episode__episode_number", "episode__participant_social", "episode__title", "episode__quote",
                     "episode__description")
    raw_id_fields = ("episode",)
    ordering = ("-episode__archived", "episode__episode_number")

admin.site.register(podcast_models.Camera, CameraAdmin)
admin.site.register(podcast_models.Episode, EpisodeAdmin)
admin.site.register(podcast_models.GetFeaturedRequest, GetFeaturedRequestAdmin)
admin.site.register(podcast_models.PodcastImage, PodcastImageAdmin)
admin.site.register(podcast_models.Requester, RequesterAdmin)
