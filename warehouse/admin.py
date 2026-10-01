from django.contrib import admin
from .models import Warehouse, InventoryItem


class InventoryInline(admin.TabularInline):
    model = InventoryItem
    extra = 1


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'state', 'total_capacity_sqft', 'status')
    list_filter = ('status', 'city')
    search_fields = ('code', 'name', 'city')
    inlines = [InventoryInline]


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('sku', 'item_name', 'warehouse', 'category', 'quantity', 'reorder_level', 'updated_at')
    list_filter = ('category', 'warehouse')
    search_fields = ('sku', 'item_name')
