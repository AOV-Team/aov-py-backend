from apps.account import models
from apps.photo import models as photo_models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from guardian import models as guardian


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
            starred_users = list()
            user_type = ContentType.objects.get_for_model(queryset[0]) if len(queryset) > 0 else None

            if user_type:
                for q in queryset:
                    interest = models.UserInterest.objects\
                        .filter(user=request.user, interest_type='star', content_type__pk=user_type.id, object_id=q.id)

                    if len(interest) > 0:
                        starred_users.append(q.id)

                return queryset.filter(id__in=starred_users)
            else:
                return queryset
        elif self.value() == 'no':
            unstarred_users = list()
            user_type = ContentType.objects.get_for_model(queryset[0]) if len(queryset) > 0 else None

            if user_type:
                for q in queryset:
                    interest = models.UserInterest.objects \
                        .filter(user=request.user, interest_type='star', content_type__pk=user_type.id, object_id=q.id)

                    if len(interest) == 0:
                        unstarred_users.append(q.id)

                return queryset.filter(id__in=unstarred_users)
            else:
                return queryset


class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')}
         ),
    )

    fieldsets = (
        ('User', {'fields': ('email', 'username', 'social_name', 'password', )}),
        ('User Details',
            {'fields': ('id', 'first_name', 'last_name', 'age', 'location', 'avatar', 'created_at', 'last_login', )}),
        ('Permissions', {'fields': ('groups', 'is_active', 'is_superuser', 'user_permissions')}),
    )

    list_display = ['username', 'email', 'social_name', 'location', 'age', 'created_at', 'photo_count',
                    'id', 'action_buttons']
    list_filter = [StarUserFilter, 'is_active', 'is_superuser']
    ordering = ['username']

    readonly_fields = ('created_at', 'id', 'last_login')

    search_fields = ['age', 'email', 'username', 'first_name', 'last_name', 'location', 'social_name']

    # Override get_changelist so we can get logged-in user
    def get_changelist(self, request, **kwargs):
        qs = super(UserAdmin, self).get_changelist(request, **kwargs)
        self.current_user = request.user
        return qs

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

        return u'<span data-content-type="users" data-id="{}" class="star-button{}fa fa-star"></span>'\
            .format(obj.id, starred)

    action_buttons.allow_tags = True
    action_buttons.short_description = 'Actions'

    def photo_count(self, obj):
        """
        Show number of photos that user has uploaded

        :param obj: instance of User
        :return: String w/ photo count
        """
        user_photos = photo_models.Photo.objects.filter(user=obj)

        return u'{}'.format(len(user_photos))

    photo_count.allow_tags = True
    photo_count.short_description = 'Photos'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'gear', 'id']
    search_fields = ['id', 'user', 'bio', 'gear']


class UserInterestAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_object', 'interest_type', 'id']
    search_fields = ['id', 'user']


class UserObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'permission', 'content_type', 'object_pk']
    search_fields = ['id', 'user', 'permission']


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.UserInterest, UserInterestAdmin)
admin.site.register(guardian.UserObjectPermission, UserObjectPermissionAdmin)
