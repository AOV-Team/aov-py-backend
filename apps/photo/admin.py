from apps.account import models as account_models
# from apps.common import forms
from apps.photo import models as photo_models
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.exceptions import ObjectDoesNotExist


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
        ('Misc', {'fields': ('attribution_name', 'photo_data',)}),
    )

    filter_horizontal = ('category', 'tag', 'photo_feed')
    # form = forms.get_image_preview_form(photo_models.Photo)

    list_display = ['photo_tag', 'user_info', 'location', 'public', 'photo_clicks', 'action_buttons', 'id']
    ordering = ['-id']
    readonly_fields = ('original_image_url',)
    search_fields = ['image', 'id']

    # Override get_changelist so we can get logged-in user
    def get_changelist(self, request, **kwargs):
        qs = super(PhotoAdmin, self).get_changelist(request, **kwargs)
        self.current_user = request.user
        return qs

    def action_buttons(self, obj):
        """
        Show action buttons

        :param obj: instance of Photo
        :return: String w/ HTML
        """
        starred = ' '

        try:
            photo_type = ContentType.objects.get_for_model(obj)
            interest = account_models.UserInterest.objects \
                .get(user=self.current_user, interest_type='star', content_type__pk=photo_type.id, object_id=obj.id)

            if interest:
                starred = ' starred '
        except ObjectDoesNotExist:
            pass

        return u'<span data-content-type="photos" data-id="{}" class="star-button{}fa fa-star"></span>' \
            .format(obj.id, starred)

    action_buttons.allow_tags = True
    action_buttons.short_description = 'Actions'

    def photo_clicks(self, obj):
        """
        Show number of photo views (clicks)

        :param obj: instance of Photo
        :return: String w/ photo view count
        """
        view_count = obj.user_action.filter(action='photo_click')

        return u'{}'.format(len(view_count))

    photo_clicks.allow_tags = True
    photo_clicks.short_description = 'Clicks'

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
