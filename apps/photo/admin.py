from apps.account import models as account_models
# from apps.common import forms
from apps.photo import forms as photo_forms
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from apps.utils.models import UserAction
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from guardian.admin import GuardedModelAdmin
import os


class FlaggedPhoto(photo_models.Photo):
    class Meta:
        proxy = True
        verbose_name = 'flagged photo'
        verbose_name_plural = 'flagged photos'


class FlaggedPhotoAdmin(admin.ModelAdmin):
    filter_horizontal = ('category', 'tag', 'photo_feed')

    list_display = ('photo_tag', 'user_info', 'public', 'location', 'photo_clicks', 'id',)
    ordering = ('-id',)
    readonly_fields = ('coordinates', 'created_at', 'location', 'original_image_url', 'photo_clicks', 'user',)
    search_fields = ('id', 'image', 'user__email', 'user__social_name', 'user__username',)

    def get_queryset(self, request):
        queryset = super(FlaggedPhotoAdmin, self).get_queryset(request)

        flag_actions = UserAction.objects.filter(action='photo_flag')

        return queryset.filter(id__in=[f.object_id for f in flag_actions])

    def has_add_permission(self, request):
        if settings.DEBUG:
            return True

        return False

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False

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


class GalleryAdmin(admin.ModelAdmin):
    """
        Admin class for Galleries

    :author: gallen
    """

    filter_horizontal = ["photos"]
    list_display = ["name", "user"]
    ordering = ["name", "user"]
    search_fields = ["name", "user", "id"]


class PhotoClassificationAdmin(GuardedModelAdmin):
    """
    Categories and tags
    """
    form = photo_forms.PhotoClassificationAdminForm
    list_display = ('name', 'classification_type', 'photo_count', 'public', 'id', 'action_buttons',)
    ordering = ['classification_type', 'name']
    search_fields = ('name', 'classification_type', 'id',)

    def get_queryset(self, request):
        return super(PhotoClassificationAdmin, self).get_queryset(request)\
            .annotate(photos_in_category=Count('category', distinct=True), photos_in_tag=Count('tag', distinct=True))

    def action_buttons(self, obj):
        """
        Show action buttons

        :param obj: instance of PhotoClassification
        :return: String w/ HTML
        """
        parameter = 'category={}'.format(obj.name)

        if obj.classification_type == 'tag':
            parameter = 'q={}'.format(obj.name)

        return u'<a class="action" href="/admin/photos/?{}"><span class="fa fa-picture-o"></span></a>' \
            .format(parameter)

    action_buttons.allow_tags = True
    action_buttons.short_description = 'Actions'

    def photo_count(self, obj):
        return obj.photos_in_category + obj.photos_in_tag

    def save_model(self, request, obj, form, change):
        post_data = request.POST
        # Check for the 'Clear' selection
        if post_data.get('category_image-clear') == 'on':
            obj.category_image = None

        if post_data.get('icon-clear') == 'on':
            obj.icon = None

        # Deal with any images added
        if obj.category_image and obj.icon:
            # Set the environment variable to overwrite files before attempting to save to remote storage
            os.environ["AWS_S3_FILE_OVERWRITE"] = "True"

            obj.category_image = Photo(obj.category_image).save("{}_background.{}".format(
                obj.name.lower(), obj.category_image.name.split('.')[-1]),
                custom_bucket=settings.STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'])
            obj.icon = Photo(obj.icon).save("{}_icon.{}".format(
                obj.name.lower(), obj.icon.name.split('.')[-1]),
                custom_bucket=settings.STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'])
        obj.save()

        # Reset the environment variable so it doesn't affect other functionalities.
        os.environ["AWS_S3_FILE_OVERWRITE"] = "False"

    photo_count.admin_order_field = 'photos'
    photo_count.short_description = 'Photos'


class PhotoCommentAdmin(admin.ModelAdmin):
    """
       Admin class for the PhotoComment model

    :author: gallen
    """

    list_display = ('id', 'photo', 'votes')
    list_display_links = ('photo', 'id')
    raw_id_fields = ('photo',)
    readonly_fields = ('user',)
    search_fields = ('user', 'id')


class PhotoFeedAdmin(GuardedModelAdmin):
    fieldsets = (
        ('Photo Feed', {'fields': ('name', 'public',)}),
    )

    list_display = ('name', 'public', 'photo_count', 'id', 'action_buttons',)
    ordering = ('name',)
    search_fields = ('name', 'id',)

    def get_queryset(self, request):
        return super(PhotoFeedAdmin, self).get_queryset(request).annotate(Count('photo'))

    def action_buttons(self, obj):
        """
        Show action buttons

        :param obj: instance of PhotoFeed
        :return: String w/ HTML
        """
        return u'<a class="action" href="/admin/photos/?feed={}"><span class="fa fa-picture-o"></span></a>' \
            .format(obj.name)

    action_buttons.allow_tags = True
    action_buttons.short_description = 'Actions'

    def photo_count(self, obj):
        return obj.photo__count

    photo_count.admin_order_field = 'photos'
    photo_count.short_description = 'Photos'


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
            return queryset.filter(user_interest__user=request.user, user_interest__interest_type='star')
        elif self.value() == 'no':
            return queryset.exclude(user_interest__user=request.user, user_interest__interest_type='star')


class PhotoAdmin(GuardedModelAdmin):
    fieldsets = (
        ('Image', {'fields': ('image', 'original_image_url', 'user', 'coordinates', 'location', 'gear', 'public', 'magazine_authorized',)}),
        ('Categorization', {'fields': ('category', 'tag', 'photo_feed')}),
        ('Misc', {'fields': ('attribution_name', 'caption', 'photo_data', 'created_at',)}),
    )

    filter_horizontal = ('category', 'tag', 'photo_feed')
    # form = forms.get_image_preview_form(photo_models.Photo)

    list_display = ('photo_tag', 'user_info', 'location', 'public', 'photo_clicks', 'action_buttons', 'id')
    list_filter = (StarPhotoFilter,)
    ordering = ('-id',)
    readonly_fields = ('coordinates', 'created_at', 'gear', 'location', 'original_image_url', 'photo_clicks', 'user',)
    search_fields = ('id', 'image', 'user__email', 'user__social_name', 'user__username',)

    # Override get_changelist so we can get logged-in user
    def get_changelist(self, request, **kwargs):
        qs = super(PhotoAdmin, self).get_changelist(request, **kwargs)
        self.current_user = request.user
        return qs

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False

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


class PhotoFeedPhoto(photo_models.Photo):
    class Meta:
        proxy = True
        verbose_name = 'feed photo'
        verbose_name_plural = 'feed photos'


class PhotoFeedPhotoFilter(admin.SimpleListFilter):
    """
    Filter to filter photos by photo feed
    """
    title = 'Feed'
    parameter_name = 'feed'

    def lookups(self, request, model_admin):
        feeds = list()

        feed_query = photo_models.PhotoFeed.objects.filter(public=True)

        for feed in feed_query:
            feeds.append((feed.id, feed.name,))

        return tuple(feeds)

    def queryset(self, request, queryset):
        try:
            if self.value():
                feed = int(self.value())

                queryset = queryset.filter(photo_feed__id=feed)
            else:
                queryset = queryset.none()
        except ValueError:
            pass

        return queryset


class PhotoFeedPhotoAdmin(admin.ModelAdmin):
    filter_horizontal = ('category', 'tag', 'photo_feed',)

    list_display = ('photo_tag', 'user_info', 'location', 'public', 'photo_clicks', 'action_buttons', 'id',)
    list_display_links = None
    list_filter = (PhotoFeedPhotoFilter,)
    readonly_fields = ('coordinates', 'created_at', 'location', 'original_image_url', 'photo_clicks', 'user',)
    search_fields = ('id', 'image', 'user__email', 'user__social_name', 'user__username',)

    def get_queryset(self, request):
        # Hackish but we need to know current photo feed ID
        self.current_feed = request.GET.get('feed')

        return super(PhotoFeedPhotoAdmin, self).get_queryset(request)\
            .extra(select={'creation_seq': 'photo_photo_photo_feed.id'})\
            .order_by('-creation_seq')

    def has_add_permission(self, request):
        if settings.DEBUG:
            return True

        return False

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False

    def action_buttons(self, obj):
        """
        Show action buttons

        :param obj: instance of PhotoFeedPhoto (Photo)
        :return: String w/ HTML
        """
        photo_feeds = ''

        for photo_feed in obj.photo_feed.all():
            photo_feeds += str(photo_feed.id) + ','

        # Since we had to disable link on image, this is the work-around
        link = urlresolvers.reverse("admin:photo_photo_change", args=[obj.id])
        edit_link = u'<a class="action" href="{}"><span class="fa fa-pencil-square"></span></a>'.format(link)

        return u'<span data-content-type="photos" data-id="{}" data-feeds="{}" data-current-feed="{}"' \
               u'class="eye-button fa fa-eye action" title="Toggle photo in this feed"></span>{}' \
            .format(obj.id, str(photo_feeds), self.current_feed, edit_link)

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


class StarredPhoto(photo_models.Photo):
    class Meta:
        proxy = True


class StarredPhotoAdmin(admin.ModelAdmin):
    filter_horizontal = ('category', 'tag', 'photo_feed')

    list_display = ('photo_tag', 'user_info', 'location', 'public', 'photo_clicks', 'action_buttons', 'id')
    ordering = ('-id',)
    readonly_fields = ('coordinates', 'created_at', 'location', 'original_image_url', 'photo_clicks', 'user',)
    search_fields = ('id', 'image', 'user__email', 'user__social_name', 'user__username',)

    def get_queryset(self, request):
        queryset = super(StarredPhotoAdmin, self).get_queryset(request)

        return queryset.filter(user_interest__user=request.user, user_interest__interest_type='star')

    def has_add_permission(self, request):
        if settings.DEBUG:
            return True

        return False

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False

    def action_buttons(self, obj):
        """
        Show action buttons

        :param obj: instance of Photo
        :return: String w/ HTML
        """
        return u'<span data-content-type="photos" data-id="{}" class="star-button starred fa fa-star"></span>'\
            .format(obj.id)

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


admin.site.register(FlaggedPhoto, FlaggedPhotoAdmin)
admin.site.register(photo_models.Gallery, GalleryAdmin)
admin.site.register(photo_models.PhotoClassification, PhotoClassificationAdmin)
admin.site.register(photo_models.PhotoComment, PhotoCommentAdmin)
admin.site.register(photo_models.PhotoFeed, PhotoFeedAdmin)
admin.site.register(photo_models.Photo, PhotoAdmin)
admin.site.register(PhotoFeedPhoto, PhotoFeedPhotoAdmin)
admin.site.register(StarredPhoto, StarredPhotoAdmin)
