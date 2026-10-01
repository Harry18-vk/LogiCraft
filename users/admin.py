from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('LogiCraft Role & Profile Details', {
            'fields': ('role', 'phone_number', 'city', 'address')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('LogiCraft Role & Profile Details', {
            'fields': ('role', 'phone_number', 'city', 'address')
        }),
    )
