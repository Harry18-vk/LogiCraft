import csv
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking
from transport.models import Schedule


@login_required
def booking_list(request):
    bookings = Booking.objects.select_related('schedule', 'schedule__route', 'user').order_by('-booking_date')
    return render(request, 'bookings/booking_list.html', {
        'bookings': bookings,
    })


@login_required
def book_ticket(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)

    if request.method == 'POST':
        passenger_name = request.POST.get('passenger_name')
        passenger_phone = request.POST.get('passenger_phone')
        passenger_email = request.POST.get('passenger_email')
        travel_date = request.POST.get('travel_date')
        seat_number = request.POST.get('seat_number')

        if schedule.available_seats > 0:
            schedule.available_seats -= 1
            schedule.save()

        booking = Booking.objects.create(
            schedule=schedule,
            user=request.user,
            passenger_name=passenger_name,
            passenger_phone=passenger_phone,
            passenger_email=passenger_email,
            travel_date=travel_date,
            seat_number=seat_number,
            fare_paid=schedule.fare,
            status=Booking.Status.CONFIRMED
        )
        messages.success(request, f"Ticket booked successfully! Ticket Number: {booking.ticket_number}")
        return redirect('bookings:booking_detail', pk=booking.pk)

    return render(request, 'bookings/book_ticket.html', {
        'schedule': schedule,
        'default_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
    })


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
    })


@login_required
def export_bookings_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logicraft_passenger_bookings.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Ticket Number', 'Passenger Name', 'Phone', 'Email',
        'Route Code', 'Source', 'Destination', 'Travel Date',
        'Departure Time', 'Seat Number', 'Fare Paid (INR)', 'Status'
    ])

    for b in Booking.objects.select_related('schedule', 'schedule__route').all():
        writer.writerow([
            b.ticket_number, b.passenger_name, b.passenger_phone, b.passenger_email or '',
            b.schedule.route.route_code, b.schedule.route.source_city, b.schedule.route.destination_city,
            b.travel_date, b.schedule.departure_time, b.seat_number, b.fare_paid, b.get_status_display()
        ])

    return response
