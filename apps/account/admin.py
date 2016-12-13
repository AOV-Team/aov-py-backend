from apps.account import models
from apps.photo import models as photo_models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from guardian import models as guardian


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
                    'id']
    list_filter = ['is_active', 'is_superuser']
    ordering = ['username']

    readonly_fields = ('created_at', 'id', 'last_login')

    search_fields = ['age', 'email', 'username', 'first_name', 'last_name', 'location', 'social_name']

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
