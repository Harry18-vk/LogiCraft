from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Route, Schedule
from fleet.models import Vehicle


@login_required
def route_list(request):
    routes = Route.objects.prefetch_related('schedules', 'schedules__vehicle').filter(is_active=True)
    inactive_routes = Route.objects.filter(is_active=False).count()
    return render(request, 'transport/route_list.html', {
        'routes': routes,
        'inactive_routes': inactive_routes,
    })


@login_required
def route_create(request):
    if request.method == 'POST':
        route_code = request.POST.get('route_code', '').strip()
        source_city = request.POST.get('source_city', '').strip()
        source_terminal = request.POST.get('source_terminal', '').strip()
        destination_city = request.POST.get('destination_city', '').strip()
        destination_terminal = request.POST.get('destination_terminal', '').strip()
        distance_km = request.POST.get('distance_km')
        estimated_duration_hours = request.POST.get('estimated_duration_hours')

        if Route.objects.filter(route_code=route_code).exists():
            messages.error(request, f"Route code '{route_code}' already exists.")
            return redirect('transport:route_create')

        Route.objects.create(
            route_code=route_code,
            source_city=source_city,
            source_terminal=source_terminal,
            destination_city=destination_city,
            destination_terminal=destination_terminal,
            distance_km=distance_km,
            estimated_duration_hours=estimated_duration_hours,
        )
        messages.success(request, f"Route {route_code} ({source_city} → {destination_city}) created successfully.")
        return redirect('transport:route_list')

    return render(request, 'transport/route_form.html', {'action': 'Create'})


@login_required
def route_edit(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        route.source_city = request.POST.get('source_city', '').strip()
        route.source_terminal = request.POST.get('source_terminal', '').strip()
        route.destination_city = request.POST.get('destination_city', '').strip()
        route.destination_terminal = request.POST.get('destination_terminal', '').strip()
        route.distance_km = request.POST.get('distance_km')
        route.estimated_duration_hours = request.POST.get('estimated_duration_hours')
        route.is_active = request.POST.get('is_active') == 'on'
        route.save()
        messages.success(request, f"Route {route.route_code} updated successfully.")
        return redirect('transport:route_list')

    return render(request, 'transport/route_form.html', {'route': route, 'action': 'Edit'})


@login_required
def route_delete(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        code = route.route_code
        route.delete()
        messages.success(request, f"Route {code} deleted successfully.")
        return redirect('transport:route_list')
    return render(request, 'transport/route_confirm_delete.html', {'route': route})


@login_required
def schedule_create(request, route_pk):
    route = get_object_or_404(Route, pk=route_pk)
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        frequency = request.POST.get('frequency')
        fare = request.POST.get('fare')
        total_seats = request.POST.get('total_seats', 40)

        vehicle = Vehicle.objects.filter(pk=vehicle_id).first() if vehicle_id else None

        Schedule.objects.create(
            route=route,
            vehicle=vehicle,
            departure_time=departure_time,
            arrival_time=arrival_time,
            frequency=frequency,
            fare=fare,
            total_seats=total_seats,
            available_seats=total_seats,
        )
        messages.success(request, f"Schedule added to route {route.route_code}.")
        return redirect('transport:route_list')

    vehicles = Vehicle.objects.filter(
        vehicle_type='PASSENGER_BUS', status='AVAILABLE'
    )
    return render(request, 'transport/schedule_form.html', {
        'route': route,
        'vehicles': vehicles,
        'frequency_choices': Schedule.Frequency.choices,
    })


@login_required
def schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle')
        schedule.vehicle = Vehicle.objects.filter(pk=vehicle_id).first() if vehicle_id else None
        schedule.departure_time = request.POST.get('departure_time')
        schedule.arrival_time = request.POST.get('arrival_time')
        schedule.frequency = request.POST.get('frequency')
        schedule.fare = request.POST.get('fare')
        schedule.total_seats = request.POST.get('total_seats', 40)
        schedule.is_active = request.POST.get('is_active') == 'on'
        schedule.save()
        messages.success(request, f"Schedule updated for route {schedule.route.route_code}.")
        return redirect('transport:route_list')

    vehicles = Vehicle.objects.filter(vehicle_type='PASSENGER_BUS')
    return render(request, 'transport/schedule_form.html', {
        'schedule': schedule,
        'route': schedule.route,
        'vehicles': vehicles,
        'frequency_choices': Schedule.Frequency.choices,
        'action': 'Edit',
    })


@login_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        route_code = schedule.route.route_code
        schedule.delete()
        messages.success(request, f"Schedule removed from route {route_code}.")
        return redirect('transport:route_list')
    return render(request, 'transport/schedule_confirm_delete.html', {'schedule': schedule})
