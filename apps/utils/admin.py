from apps.utils import models as utils_models
from django.conf import settings
from django.contrib import admin


class UserActionAdmin(admin.ModelAdmin):
    list_display = ('action', 'id', 'user', 'object_id',)
    readonly_fields = ('user', 'action', 'content_type', 'object_id',)
    search_fields = ('action', 'user', 'id',)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False


admin.site.register(utils_models.UserAction, UserActionAdmin)



