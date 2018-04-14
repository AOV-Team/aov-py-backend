from apps.utils import models as utils_models
from django.conf import settings
from django.contrib import admin
# from rest_framework_tracking.admin import APIRequestLogAdmin
# from rest_framework_tracking.models import APIRequestLog


class UserActionAdmin(admin.ModelAdmin):
    list_display = ('action', 'id', 'user', 'object_id',)
    readonly_fields = ('user', 'action', 'content_type', 'object_id',)
    search_fields = ('action', 'user', 'id',)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False
#
# class MyAPIRequestLogAdmin(APIRequestLogAdmin):
#     date_hierarchy = 'requested_at'
#     list_display = ('id', 'requested_at', 'response_ms', 'status_code',
#                     'user', 'method',
#                     'path', 'remote_addr', 'host',
#                     'query_params')
#     list_filter = ('method', 'status_code')
#     search_fields = ('path', 'user__email',)
#     raw_id_fields = ('user', )
#
#
# admin.site.unregister(APIRequestLog)
# admin.site.register(APIRequestLog, MyAPIRequestLogAdmin)

admin.site.register(utils_models.UserAction, UserActionAdmin)
