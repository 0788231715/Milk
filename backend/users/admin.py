from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ManagerPermission

class ManagerPermissionInline(admin.StackedInline):
    model = ManagerPermission
    can_delete = False
    verbose_name_plural = 'Manager Permissions'

class CustomUserAdmin(UserAdmin):
    inlines = (ManagerPermissionInline,)
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'phone_number')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(ManagerPermission)
