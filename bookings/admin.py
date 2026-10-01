from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'passenger_name', 'schedule', 'travel_date', 'seat_number', 'fare_paid', 'status')
    list_filter = ('status', 'travel_date')
    search_fields = ('ticket_number', 'passenger_name', 'passenger_phone')
    readonly_fields = ('ticket_number', 'booking_date')
