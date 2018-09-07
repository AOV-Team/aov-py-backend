from apps.utils import models as utils_models
from datetime import datetime
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from rangefilter.filter import DateRangeFilter


class UserActionAdmin(admin.ModelAdmin):
    list_display = ('action', 'id', 'user', 'object_id',)
    readonly_fields = ('user', 'action', 'content_type', 'object_id',)
    search_fields = ('action', 'user', 'id',)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False


class UserFeedbackAdmin(admin.ModelAdmin):
    actions = ["download_csv", "send_reply"]
    list_display = ('user', 'feedback_type', 'created_at', 'has_reply', 'reply_timestamp')
    list_filter = (
        ('created_at', DateRangeFilter),
        ('feedback_type', admin.ChoicesFieldListFilter),
    )
    readonly_fields = ('user',)
    search_fields = ('feedback_type', 'user', 'id',)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False

    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from io import StringIO

        f = StringIO()
        writer = csv.writer(f)

        writer.writerow(["Submitted", "Type", "Username", "Email", "Message", "Has Reply", "Reply", "Replied On"])

        for created_at, feedback_type, username, email, message, has_reply, reply, reply_timestamp in queryset.values_list(
                'created_at', 'feedback_type', 'user__username', 'user__email', 'message', 'has_reply', 'reply',
                'reply_timestamp'):

            created_at = datetime.strftime(created_at, "%Y-%m-%d")
            reply_timestamp = datetime.strftime(reply_timestamp, "%Y-%m-%d")

            if feedback_type == "A":
                feedback_type = "Appreciation"

            if feedback_type == "B":
                feedback_type = "Bug"

            if feedback_type == "F":
                feedback_type = "Feature Request"

            writer.writerow([created_at, feedback_type, username, email, message, has_reply, reply, reply_timestamp])

        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=user_feedback{}.csv'.format(
            timezone.now().date().isoformat())
        return response

    download_csv.short_description = "Download Feedback Objects as CSV"

    def send_reply(self, request, queryset):
        if 'apply' in request.POST:
            import requests
            from apps.common.test.helpers import get_token_for_user
            auth_token = get_token_for_user(request.user)
            headers = {"authorization": "Token {}".format(auth_token)}

            base_url_lut = {
                "local": "http://localhost:8000/api",
                "staging": "https://staging.artofvisuals.com/api",
                "production": "https://data.artofvisuals.com/api"
            }

            url_base = ""
            
            request_url = request.build_absolute_uri(request.get_full_path())

            if "localhost" in request_url:
                url_base = base_url_lut["local"]

            if "staging" in request_url:
                url_base = base_url_lut["staging"]

            if "production" in request_url:
                url_base = base_url_lut["production"]

            payload = {
                "feedback_type": "reply",
                "reply": request.POST.get("reply-text")
            }

            for pk in queryset.exclude(has_reply=True).values_list("id", flat=True):
                requests.post(url_base + "/utils/feedback/{}/reply".format(pk), data=payload, headers=headers)

            self.message_user(request, "Replied to {} feedback items".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())

        return render(request, 'feedback_reply.html', context={ "feedback_items": queryset})



admin.site.register(utils_models.UserAction, UserActionAdmin)
admin.site.register(utils_models.Feedback, UserFeedbackAdmin)
