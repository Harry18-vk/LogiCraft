from django.db import models
from django.conf import settings


class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        HEAVY_TRUCK = 'HEAVY_TRUCK', 'Heavy Cargo Truck (20-40T)'
        MEDIUM_TRUCK = 'MEDIUM_TRUCK', 'Medium Transport Truck (5-15T)'
        DELIVERY_VAN = 'DELIVERY_VAN', 'Delivery Van / Light Commercial'
        PASSENGER_BUS = 'PASSENGER_BUS', 'Public Transit Bus'
        CONTAINER = 'CONTAINER', 'Intermodal Container Carrier'

    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        ON_TRIP = 'ON_TRIP', 'On Trip / In Transit'
        IN_MAINTENANCE = 'IN_MAINTENANCE', 'In Maintenance'
        RETIRED = 'RETIRED', 'Retired'

    class FuelType(models.TextChoices):
        DIESEL = 'DIESEL', 'Diesel'
        PETROL = 'PETROL', 'Petrol'
        ELECTRIC = 'ELECTRIC', 'Electric'
        CNG = 'CNG', 'CNG'

    reg_number = models.CharField(max_length=30, unique=True, verbose_name="Registration Number")
    model_name = models.CharField(max_length=100, help_text="e.g. Tata Signa 4825.TK or Volvo 9400")
    vehicle_type = models.CharField(max_length=30, choices=VehicleType.choices, default=VehicleType.MEDIUM_TRUCK)
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum cargo payload in KG")
    passenger_capacity = models.PositiveIntegerField(default=0, help_text="Passenger seating capacity (if bus)")
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices, default=FuelType.DIESEL)
    odometer_km = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    status = models.CharField(max_length=25, choices=Status.choices, default=Status.AVAILABLE)
    current_location = models.CharField(max_length=150, blank=True, null=True, help_text="Current city or GPS waypoint")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=28.6139, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=77.2090, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reg_number} ({self.get_vehicle_type_display()}) - {self.get_status_display()}"


class Driver(models.Model):
    class Status(models.TextChoices):
        ON_DUTY = 'ON_DUTY', 'On Duty (Available)'
        OFF_DUTY = 'OFF_DUTY', 'Off Duty'
        ON_TRIP = 'ON_TRIP', 'On Trip'
        ON_LEAVE = 'ON_LEAVE', 'On Leave'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='driver_profile'
    )
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    years_of_experience = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ON_DUTY)
    assigned_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_drivers'
    )
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Driver {self.user.get_full_name() or self.user.username} (Lic: {self.license_number})"


class MaintenanceRecord(models.Model):
    class ServiceType(models.TextChoices):
        ROUTINE = 'ROUTINE', 'Routine Preventive Service'
        ENGINE = 'ENGINE', 'Engine Overhaul / Powertrain'
        TIRES = 'TIRES', 'Tire Rotation / Replacement'
        BRAKES = 'BRAKES', 'Brake System Service'
        INSPECTION = 'INSPECTION', 'Safety & Emissions Inspection'
        EMERGENCY = 'EMERGENCY', 'Roadside Breakdown Repair'

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_logs')
    service_type = models.CharField(max_length=30, choices=ServiceType.choices, default=ServiceType.ROUTINE)
    description = models.TextField()
    service_date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    odometer_at_service = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Maint #{self.id} - {self.vehicle.reg_number} ({self.get_service_type_display()})"
