from apps.communication import models as communication_models
from django.contrib import admin


class PushMessageAdmin(admin.ModelAdmin):
    list_display = ('send_at', 'id',)
    search_fields = ('id', 'message',)

admin.site.register(communication_models.PushMessage, PushMessageAdmin)
