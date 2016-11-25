from apps.account import models
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

    list_display = ['username', 'email', 'social_name', 'is_active', 'id']
    list_filter = ['is_active', 'is_superuser']
    ordering = ['username']

    readonly_fields = ('created_at', 'id', 'last_login')

    search_fields = ['email', 'username', 'first_name', 'last_name']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'id']
    search_fields = ['id', 'user', 'bio']


class UserObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'permission', 'content_type', 'object_pk']
    search_fields = ['id', 'user', 'permission']


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(guardian.UserObjectPermission, UserObjectPermissionAdmin)
