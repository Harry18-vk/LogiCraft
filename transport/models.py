from django.db import models
from fleet.models import Vehicle


class Route(models.Model):
    route_code = models.CharField(max_length=20, unique=True, verbose_name="Route Number / Code")
    source_city = models.CharField(max_length=100)
    source_terminal = models.CharField(max_length=150, help_text="e.g. ISBT Kashmiri Gate")
    destination_city = models.CharField(max_length=100)
    destination_terminal = models.CharField(max_length=150, help_text="e.g. Agra Cantt Bus Station")
    distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_duration_hours = models.DecimalField(max_digits=5, decimal_places=2, help_text="Duration in hours")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.route_code}] {self.source_city} ➔ {self.destination_city} ({self.distance_km} km)"


class Schedule(models.Model):
    class Frequency(models.TextChoices):
        DAILY = 'DAILY', 'Daily'
        WEEKDAYS = 'WEEKDAYS', 'Monday to Friday'
        WEEKENDS = 'WEEKENDS', 'Saturday & Sunday'
        SPECIAL = 'SPECIAL', 'Special Service'

    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Assigned Bus",
        related_name='transport_schedules'
    )
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.DAILY)
    fare = models.DecimalField(max_digits=8, decimal_places=2, help_text="Ticket price in INR")
    total_seats = models.PositiveIntegerField(default=40)
    available_seats = models.PositiveIntegerField(default=40)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.route.route_code}: Departs {self.departure_time} - Rs.{self.fare}"
