from apps.account import models as account_models
# from apps.common import forms
from apps.photo import models as photo_models
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count


class PhotoClassificationAdmin(admin.ModelAdmin):
    """
    Categories and tags
    """
    list_display = ('name', 'classification_type', 'photo_count', 'public', 'id',)
    ordering = ('classification_type', 'name',)
    search_fields = ('name', 'classification_type', 'id',)

    def get_queryset(self, request):
        return super(PhotoClassificationAdmin, self).get_queryset(request)\
            .annotate(photos_in_category=Count('category'), photos_in_tag=Count('tag'))

    def photo_count(self, obj):
        return obj.photos_in_category + obj.photos_in_tag

    photo_count.admin_order_field = 'photos'
    photo_count.short_description = 'Photos'


class PhotoFeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'public', 'id']
    ordering = ['name']
    search_fields = ['name', 'id']


class StarPhotoFilter(admin.SimpleListFilter):
    """
    Filter to filter by photos that have/have not been starred by logging user
    """
    title = 'Starred'
    parameter_name = 'starred'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Starred'),
            ('no', 'Unstarred')
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            starred_photos = list()
            photo_type = ContentType.objects.get_for_model(queryset[0]) if len(queryset) > 0 else None

            if photo_type:
                for q in queryset:
                    interest = account_models.UserInterest.objects\
                        .filter(user=request.user, interest_type='star', content_type__pk=photo_type.id, object_id=q.id)

                    if len(interest) > 0:
                        starred_photos.append(q.id)

                return queryset.filter(id__in=starred_photos)
            else:
                return queryset
        elif self.value() == 'no':
            unstarred_photos = list()
            photo_type = ContentType.objects.get_for_model(queryset[0]) if len(queryset) > 0 else None

            if photo_type:
                for q in queryset:
                    interest = account_models.UserInterest.objects \
                        .filter(user=request.user, interest_type='star', content_type__pk=photo_type.id, object_id=q.id)

                    if len(interest) == 0:
                        unstarred_photos.append(q.id)

                return queryset.filter(id__in=unstarred_photos)
            else:
                return queryset


class PhotoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Image', {'fields': ('image', 'original_image_url', 'user', 'location', 'public',)}),
        ('Categorization', {'fields': ('category', 'tag', 'photo_feed')}),
        ('Misc', {'fields': ('attribution_name', 'photo_data', 'created_at',)}),
    )

    filter_horizontal = ('category', 'tag', 'photo_feed')
    # form = forms.get_image_preview_form(photo_models.Photo)

    list_display = ['photo_tag', 'user_info', 'location', 'public', 'photo_clicks', 'action_buttons', 'id']
    list_filter = (StarPhotoFilter,)
    ordering = ['-id']
    readonly_fields = ('created_at', 'original_image_url',)
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
