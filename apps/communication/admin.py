from apps.communication import models as communication_models
from django.contrib import admin


class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'message_count', 'get_participants')
    search_fields = ('id', 'participants__email', 'participants__username')

    def get_participants(self, obj):
        participants = obj.participants.all()

        return ["{}, {}\n".format(p.email, p.username) for p in participants]

    get_participants.short_description = "Participants"


class PushMessageAdmin(admin.ModelAdmin):
    list_display = ('send_at', 'id',)
    search_fields = ('id', 'message',)


class PushNotificationRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "receiver", "sender",)
    search_fields = ("id", "message", "receiver__user__email", "sender__email", "sender__username",
                     "receiver__user__username",)

admin.site.register(communication_models.Conversation, ConversationAdmin)
admin.site.register(communication_models.PushMessage, PushMessageAdmin)
admin.site.register(communication_models.PushNotificationRecord, PushNotificationRecordAdmin)
