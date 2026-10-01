from django.db import models


class Warehouse(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active / Operating'
        NEAR_CAPACITY = 'NEAR_CAPACITY', 'Near Full Capacity'
        MAINTENANCE = 'MAINTENANCE', 'Under Maintenance'
        INACTIVE = 'INACTIVE', 'Inactive'

    code = models.CharField(max_length=20, unique=True, verbose_name="Warehouse Code")
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    address = models.TextField()
    total_capacity_sqft = models.DecimalField(max_digits=12, decimal_places=2, default=50000.0)
    manager_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=28.6139)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=77.2090)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} [{self.code}] - {self.city}"

    @property
    def total_inventory_count(self):
        return sum(item.quantity for item in self.inventory_items.all())


class InventoryItem(models.Model):
    class Category(models.TextChoices):
        ELECTRONICS = 'ELECTRONICS', 'Electronics & Gadgets'
        PERISHABLE = 'PERISHABLE', 'Perishable Goods / Cold Chain'
        INDUSTRIAL = 'INDUSTRIAL', 'Industrial & Heavy Equipment'
        RETAIL = 'RETAIL', 'Consumer Retail & Apparel'
        PHARMACEUTICAL = 'PHARMACEUTICAL', 'Pharmaceuticals & Medical'

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory_items')
    sku = models.CharField(max_length=50, verbose_name="SKU Code")
    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.RETAIL)
    quantity = models.PositiveIntegerField(default=0)
    unit_weight_kg = models.DecimalField(max_digits=8, decimal_places=2, default=1.0)
    reorder_level = models.PositiveIntegerField(default=50, help_text="Minimum stock alert threshold")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('warehouse', 'sku')

    def __str__(self):
        return f"{self.item_name} ({self.sku}) - Qty: {self.quantity} at {self.warehouse.code}"
