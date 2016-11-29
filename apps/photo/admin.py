from apps.common import forms
from apps.photo import models as photo_models
from django.contrib import admin


class PhotoClassificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'classification_type', 'public', 'id']
    search_fields = ['name', 'classification_type', 'id']


class PhotoFeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'public', 'id']
    ordering = ['name']
    search_fields = ['name', 'id']


class PhotoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Image', {'fields': ('image_preview', 'image', 'user', 'location', 'public')}),
        ('Categorization', {'fields': ('category', 'tag', 'photo_feed')}),
        ('Misc', {'fields': ('attribution_name', 'photo_data')}),
    )

    filter_horizontal = ('category', 'tag', 'photo_feed')
    form = forms.get_image_preview_form(photo_models.Photo)

    list_display = ['user', 'location', 'public', 'id']
    ordering = ['-id']
    search_fields = ['image', 'id']


admin.site.register(photo_models.PhotoClassification, PhotoClassificationAdmin)
admin.site.register(photo_models.PhotoFeed, PhotoFeedAdmin)
admin.site.register(photo_models.Photo, PhotoAdmin)
