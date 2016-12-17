from apps.utils import models as utils_models
from django.contrib import admin


class UserActionAdmin(admin.ModelAdmin):
    list_display = ('action', 'id', 'user', 'object_id',)
    readonly_fields = ('user', 'action', 'content_type', 'object_id',)
    search_fields = ('action', 'user', 'id',)


admin.site.register(utils_models.UserAction, UserActionAdmin)



