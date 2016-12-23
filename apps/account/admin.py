from apps.account import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from guardian import models as guardian
from guardian.admin import GuardedModelAdmin


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
        ('Permissions', {'fields': ('groups', 'is_active', 'is_admin', 'is_superuser', 'user_permissions')}),
    )

    list_display = ('username', 'email', 'social_name', 'location', 'age', 'photo_count', 'id', 'created_at',
                    'action_buttons',)
    list_filter = (StarUserFilter, 'is_active', 'is_superuser',)
    list_per_page = 100
    ordering = ('-photo__count', '-id', 'username',)

    readonly_fields = ('created_at', 'id', 'last_login', 'photo_count',)

    search_fields = ['age', 'email', 'username', 'first_name', 'last_name', 'location', 'social_name']

    # Override get_changelist so we can get logged-in user
    def get_changelist(self, request, **kwargs):
        qs = super(UserAdmin, self).get_changelist(request, **kwargs)
        self.current_user = request.user
        return qs

    def get_queryset(self, request):
        return super(UserAdmin, self).get_queryset(request).annotate(photos=Count('photo'))

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

        photo_link = u'<a class="action" href="/admin/photos/?u={}"><span class="fa fa-picture-o"></span></a>'\
            .format(obj.username)

        return u'<span data-content-type="users" data-id="{}" class="action star-button{}fa fa-star"></span>{}'\
            .format(obj.id, starred, photo_link)

    action_buttons.allow_tags = True
    action_buttons.short_description = 'Actions'

    def photo_count(self, obj):
        return obj.photos

    photo_count.admin_order_field = 'photo__count'
    photo_count.short_description = 'Photos'


class ProfileAdmin(GuardedModelAdmin):
    list_display = ('user', 'bio', 'gear', 'id',)
    readonly_fields = ('gear', 'user',)
    search_fields = ('id', 'user', 'bio', 'gear',)

    # Not needed if user is readonly
    # def render_change_form(self, request, context, *args, **kwargs):
    #     """
    #     Fixes issue where form won't render due to annotation
    #     """
    #     context['adminform'].form.fields['user'].queryset = models.User.objects.all()
    #     return super(ProfileAdmin, self).render_change_form(request, context, args, kwargs)


class UserInterestAdmin(GuardedModelAdmin):
    list_display = ('content_type', 'id', 'content_object', 'interest_type', 'user',)
    readonly_fields = ('user', 'interest_type', 'content_type', 'object_id',)
    search_fields = ('id', 'user',)


class UserObjectPermissionAdmin(GuardedModelAdmin):
    list_display = ['id', 'user', 'permission', 'content_type', 'object_pk']
    search_fields = ['id', 'user', 'permission']


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.UserInterest, UserInterestAdmin)
admin.site.register(guardian.UserObjectPermission, UserObjectPermissionAdmin)
