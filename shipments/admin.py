from django.contrib import admin
from .models import Shipment, ShipmentStatusHistory


class TimelineInline(admin.TabularInline):
    model = ShipmentStatusHistory
    extra = 1
    readonly_fields = ('timestamp',)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        'tracking_number', 'sender_name', 'receiver_name',
        'current_status', 'weight_kg', 'assigned_vehicle',
        'assigned_driver', 'estimated_delivery'
    )
    list_filter = ('current_status', 'origin_warehouse', 'destination_warehouse')
    search_fields = ('tracking_number', 'sender_name', 'receiver_name', 'receiver_phone')
    readonly_fields = ('tracking_number', 'created_at', 'updated_at')
    inlines = [TimelineInline]


@admin.register(ShipmentStatusHistory)
class ShipmentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'status', 'location_checkpoint', 'timestamp', 'updated_by')
    list_filter = ('status', 'timestamp')
    search_fields = ('shipment__tracking_number', 'location_checkpoint')
