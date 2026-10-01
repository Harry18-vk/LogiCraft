from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'System Administrator'
        LOGISTICS_MANAGER = 'LOGISTICS_MANAGER', 'Logistics Manager'
        DRIVER = 'DRIVER', 'Fleet Driver'
        CUSTOMER = 'CUSTOMER', 'Customer / Passenger'

    role = models.CharField(
        max_length=25,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text='Designates the role and permissions of the user in LogiCraft.'
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_logistics_manager(self):
        return self.role == self.Role.LOGISTICS_MANAGER

    @property
    def is_driver(self):
        return self.role == self.Role.DRIVER

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
