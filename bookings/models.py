import uuid
from django.db import models
from django.conf import settings
from transport.models import Schedule


def generate_ticket_number():
    return f"TKT-{uuid.uuid4().hex[:7].upper()}"


class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        COMPLETED = 'COMPLETED', 'Journey Completed'

    ticket_number = models.CharField(
        max_length=30,
        unique=True,
        default=generate_ticket_number,
        editable=False
    )
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transport_bookings'
    )
    passenger_name = models.CharField(max_length=150)
    passenger_phone = models.CharField(max_length=25)
    passenger_email = models.EmailField(blank=True, null=True)
    travel_date = models.DateField()
    seat_number = models.CharField(max_length=10)
    fare_paid = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket_number} - {self.passenger_name} ({self.schedule.route.route_code})"
