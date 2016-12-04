# from apps.common import forms
from apps.photo import models as photo_models
from django.contrib import admin
from django.core import urlresolvers


class PhotoClassificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'classification_type', 'public', 'id']
    search_fields = ['name', 'classification_type', 'id']


class PhotoFeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'public', 'id']
    ordering = ['name']
    search_fields = ['name', 'id']


class PhotoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Image', {'fields': ('image', 'original_image_url', 'user', 'location', 'public',)}),
        ('Categorization', {'fields': ('category', 'tag', 'photo_feed')}),
        ('Misc', {'fields': ('attribution_name', 'photo_data')}),
    )

    filter_horizontal = ('category', 'tag', 'photo_feed')
    # form = forms.get_image_preview_form(photo_models.Photo)

    list_display = ['photo_tag', 'user_info', 'location', 'public', 'id']
    ordering = ['-id']
    readonly_fields = ('original_image_url',)
    search_fields = ['image', 'id']

    def user_info(self, obj):
        if obj.user:
            link = urlresolvers.reverse("admin:account_user_change", args=[obj.user.id])
            return u'<a href="{}">{} / {}</a>'.format(link, obj.user.username, obj.user.social_name)
        else:
            return '--empty--'

    user_info.allow_tags = True
    user_info.short_description = 'Username / Social Name'


admin.site.register(photo_models.PhotoClassification, PhotoClassificationAdmin)
admin.site.register(photo_models.PhotoFeed, PhotoFeedAdmin)
admin.site.register(photo_models.Photo, PhotoAdmin)
