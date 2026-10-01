from django.contrib import admin
from .models import Vehicle, Driver, MaintenanceRecord


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('reg_number', 'model_name', 'vehicle_type', 'capacity_kg', 'passenger_capacity', 'status', 'current_location')
    list_filter = ('vehicle_type', 'status', 'fuel_type')
    search_fields = ('reg_number', 'model_name', 'current_location')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'years_of_experience', 'status', 'assigned_vehicle')
    list_filter = ('status',)
    search_fields = ('user__username', 'license_number')


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'service_type', 'service_date', 'cost', 'status')
    list_filter = ('service_type', 'status', 'service_date')
    search_fields = ('vehicle__reg_number', 'description')
