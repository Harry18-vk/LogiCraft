import uuid
from django.db import models
from django.conf import settings
from fleet.models import Vehicle, Driver
from warehouse.models import Warehouse


def generate_tracking_number():
    return f"LC-{uuid.uuid4().hex[:8].upper()}"


class Shipment(models.Model):
    class Status(models.TextChoices):
        BOOKED = 'BOOKED', 'Booked & Registered'
        PICKED_UP = 'PICKED_UP', 'Picked Up from Shipper'
        AT_HUB = 'AT_HUB', 'Sorted at Logistics Hub'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'Out for Delivery'
        DELIVERED = 'DELIVERED', 'Delivered Successfully'
        RETURNED = 'RETURNED', 'Returned to Origin'
        CANCELLED = 'CANCELLED', 'Cancelled'

    tracking_number = models.CharField(
        max_length=40,
        unique=True,
        default=generate_tracking_number,
        editable=False,
        verbose_name="Tracking Number"
    )
    sender_name = models.CharField(max_length=150)
    sender_phone = models.CharField(max_length=25)
    sender_address = models.TextField()

    receiver_name = models.CharField(max_length=150)
    receiver_phone = models.CharField(max_length=25)
    receiver_address = models.TextField()

    origin_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outgoing_shipments'
    )
    destination_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_shipments'
    )

    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total parcel weight in kg")
    description = models.CharField(max_length=255, help_text="Summary of contents")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    assigned_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipments'
    )
    assigned_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='driver_shipments'
    )

    current_status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.BOOKED
    )
    estimated_delivery = models.DateField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_shipments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tracking_number} - {self.receiver_name} ({self.get_current_status_display()})"


class ShipmentStatusHistory(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='timeline')
    status = models.CharField(max_length=25, choices=Shipment.Status.choices)
    location_checkpoint = models.CharField(max_length=150, help_text="City, Hub or GPS checkpoint")
    notes = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipment.tracking_number}: {self.status} at {self.location_checkpoint}"
