from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for the CustomUser model."""
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    # Use email field instead of username
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'profile_picture', 'phone_number', 'address', 'date_of_birth')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2'), # Add password confirmation field for creation
        }),
    )

    # Override the default username field
    readonly_fields = ('last_login', 'date_joined')
