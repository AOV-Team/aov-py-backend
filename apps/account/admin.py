from apps.account import models
from apps.photo import models as photo_models
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils.html import format_html
from guardian import models as guardian
from guardian.admin import GuardedModelAdmin
from push_notifications.admin import DeviceAdmin
from push_notifications.models import APNSDevice


class APNSDeviceAdmin(DeviceAdmin):
    readonly_fields = ('user',)


class GearAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Gear', {'fields': ('item_make', 'item_model', 'link', 'id',)}),
        ('Misc', {'fields': ('public', 'reviewed',)}),
    )

    list_display = ('name', 'link', 'public', 'reviewed',)
    list_filter = ('public', 'reviewed',)
    ordering = ('item_make', 'item_model',)
    readonly_fields = ('id',)
    search_fields = ('item_make', 'item_model', 'link', 'name')

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False


class StarredUser(models.User):
    class Meta:
        proxy = True


class StarredUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'social_name', 'location', 'age', 'photo_count', 'id', 'action_buttons')

    list_filter = ('is_active',)
    list_per_page = 100
    ordering = ('-photo_user__count', '-id', 'username',)

    readonly_fields = ('created_at', 'id', 'last_login', 'photo_count',)

    search_fields = ('age', 'email', 'username', 'first_name', 'last_name', 'location', 'social_name',)

    def get_queryset(self, request):
        queryset = models.User.objects.none()

        user_type = ContentType.objects.get_for_model(models.User)
        interests = models.UserInterest.objects.filter(user=request.user, interest_type='star', content_type=user_type)

        for i in interests:
            queryset = queryset | models.User.objects.filter(id=i.object_id)

        return queryset.annotate(Count('photo_user'))

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

        :param obj: instance of User
        :return: String w/ HTML
        """
        photo_link = format_html(
            '<a class="action" href="/admin/photos/?u={}"><span class="fa fa-picture-o"></span></a>', obj.username)

        return format_html(
            '<span data-content-type="users" data-id="{}" class="action star-button starred fa fa-star"></span>{}',
            obj.id, photo_link)

    action_buttons.allow_tags = True
    action_buttons.short_description = 'Actions'

    def photo_count(self, obj):
        return obj.photo_user__count

    photo_count.admin_order_field = 'photo_user__count'
    photo_count.short_description = 'Photos'


class StarUserFilter(admin.SimpleListFilter):
    """
    Filter to filter by users that have/have not been starred by logging user
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
            q = models.User.objects.none()
            user_type = ContentType.objects.get_for_model(models.User)
            interests = models.UserInterest.objects.filter(user=request.user, interest_type='star',
                                                           content_type=user_type)

            for i in interests:
                q = q | queryset.filter(id=i.object_id)

            return q.annotate(Count('photo_user'))
        elif self.value() == 'no':
            unstarred_users = list()
            user_type = ContentType.objects.get_for_model(models.User)
            interests = models.UserInterest.objects.filter(user=request.user, interest_type='star',
                                                           content_type=user_type)

            for i in interests:
                unstarred_users.append(i.object_id)

            return queryset.exclude(id__in=unstarred_users).annotate(Count('photo_user'))


class PowerUserFilter(admin.SimpleListFilter):
    """
        Filter to filter users based on their qualifications as power users
    """
    title = 'Power User'
    parameter_name = 'power_user'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Power User'),
            ('no', 'Standard User')
        )

    def queryset(self, request, queryset):
        users = queryset.filter(
            is_active=True, age__isnull=False, age__gte=1)
        cutoff = datetime.now() - timedelta(days=7)
        sessions = models.UserSession.objects.filter(user__in=users, modified_at__gte=cutoff)
        power_users = models.User.objects.filter(id__in=sessions.values_list("user", flat=True))
        power_users = power_users.annotate(Count("usersession")).filter(usersession__count__gte=3)

        if self.value() == 'yes':
            if power_users.count() == 0:
                return models.User.objects.none().annotate(Count('photo_user')).annotate(Count('follower'))
            return power_users.annotate(Count('photo_user')).annotate(Count('follower'))

        elif self.value() == 'no':
            power_user_ids = power_users.values_list("id", flat=True)
            q = users.exclude(id__in=power_user_ids)

            return q.annotate(Count('photo_user')).annotate(Count('follower'))


class UserAdmin(BaseUserAdmin):
    actions = ['download_csv']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')}
         ),
    )

    fieldsets = (
        ('User', {'fields': ('email', 'username', 'social_name', 'password', )}),
        ('User Details',
            {'fields': ('first_name', 'last_name', 'age', 'gender', 'location', 'avatar', 'created_at', 'last_login',
                        'gear', 'follower', 'social_url', 'website_url', 'signup_source',)}),
        ('Permissions', {'fields': ('groups', 'is_active', 'is_admin', 'is_superuser', 'user_permissions')}),
    )

    list_display = ('username', 'email', 'social_name', 'location', 'age', 'gender', 'followers_count', 'photo_count', 'id',
                    'created_at', 'action_buttons',)
    list_filter = (StarUserFilter, PowerUserFilter, 'is_active', 'is_superuser',)
    list_per_page = 100
    ordering = ('-photo_user__count', '-follower__count', '-id', 'username',)

    readonly_fields = ('created_at', 'gear', 'id', 'follower', 'last_login', 'photo_count',)
    search_fields = ('age', 'email', 'username', 'first_name', 'last_name', 'location', 'social_name',)

    # Override get_changelist so we can get logged-in user
    def get_changelist(self, request, **kwargs):
        qs = super(UserAdmin, self).get_changelist(request, **kwargs)
        self.current_user = request.user
        return qs

    def get_queryset(self, request):
        return super(UserAdmin, self).get_queryset(request).annotate(
            Count('photo_user')).annotate(Count('follower', distinct=True))

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG or request.user.is_superuser:
            return True

        return False

    def action_buttons(self, obj):
        """
        Show action buttons

        :param obj: instance of User
        :return: String w/ HTML
        """
        starred = ' '

        try:
            user_type = ContentType.objects.get_for_model(obj)
            interest = models.UserInterest.objects \
                .get(user=self.current_user, interest_type='star', content_type__pk=user_type.id, object_id=obj.id)

            if interest:
                starred = ' starred '
        except ObjectDoesNotExist:
            pass

        photo_link = format_html(
            '<a class="action" href="/admin/photos/?u={}"><span class="fa fa-picture-o"></span></a>', obj.username)

        location_history_link = format_html(
            '<a class="action" href="/admin/account/userlocation/?user_id={}"><span class="fa fa-map-marker"></span></a>',
            obj.id)

        return format_html('<span data-content-type="users" data-id="{}" class="action star-button{}fa fa-star"></span>{}{}',
                           obj.id, starred, photo_link, location_history_link)

    action_buttons.allow_tags = True
    action_buttons.short_description = 'Actions'

    def followers_count(self, obj):
        return obj.follower__count

    followers_count.admin_order_field = 'follower__count'
    followers_count.short_description = 'Followers'

    def photo_count(self, obj):
        return obj.photo_user__count

    photo_count.admin_order_field = 'photo_user__count'
    photo_count.short_description = 'Photos'

    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from io import StringIO

        queryset = queryset.exclude(email__icontains="test").exclude(email__icontains="Anonymous")
        f = StringIO()
        writer = csv.writer(f)

        writer.writerow(["Username", "Email", "First Name", "Last Name", "Location", "# of Photo Uploads"])

        for id, username, email, first_name, last_name, location in queryset.values_list(
                'id', 'username', 'email', 'first_name', 'last_name', 'location'):
            photos = photo_models.Photo.objects.filter(user_id=id).count()
            writer.writerow([username, first_name, last_name, email, location, photos])

        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=users.csv'
        return response

    download_csv.short_description = "Download CSV file for selected users"


class ProfileAdmin(GuardedModelAdmin):
    list_display = ('user', 'bio', 'id',)
    readonly_fields = ('user',)
    search_fields = ('id', 'bio', 'user__email', 'user__first_name', 'user__last_name', 'user__social_name',
                     'user__username',)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG or request.user.is_superuser:
            return True

        return False


class UserInterestAdmin(GuardedModelAdmin):
    list_display = ('content_type', 'id', 'content_object', 'interest_type', 'user',)
    readonly_fields = ('user', 'interest_type', 'content_type', 'object_id',) if not settings.DEBUG else tuple()
    search_fields = ('id', 'user',)

    def render_change_form(self, request, context, *args, **kwargs):
        """
        Fixes issue where form won't render due to annotation
        """
        context['adminform'].form.fields['user'].queryset = models.User.objects.all()
        return super(UserInterestAdmin, self).render_change_form(request, context, args, kwargs)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False


class UserObjectPermissionAdmin(GuardedModelAdmin):
    list_display = ('id', 'user', 'permission', 'content_type', 'object_pk',)
    search_fields = ('id', 'user', 'permission',)

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True

        return False


class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'coordinates', 'location', 'created_at')
    search_fields = ('id', 'user', 'location')

    def render_change_form(self, request, context, *args, **kwargs):
        """
        Fixes issue where form won't render due to annotation
        """
        context['adminform'].form.fields['user'].queryset = models.User.objects.all()
        return super(UserLocationAdmin, self).render_change_form(request, context, args, kwargs)


class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user",)
    readonly_fields = ("session_key", "user",)
    search_fields = ("user",)


admin.site.register(models.Gear, GearAdmin)
admin.site.register(StarredUser, StarredUserAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.UserInterest, UserInterestAdmin)
admin.site.register(guardian.UserObjectPermission, UserObjectPermissionAdmin)
admin.site.unregister(APNSDevice)
admin.site.register(APNSDevice, APNSDeviceAdmin)
admin.site.register(models.UserLocation, UserLocationAdmin)
admin.site.register(models.UserSession, UserSessionAdmin)
