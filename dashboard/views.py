from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from fleet.models import Vehicle, Driver, MaintenanceRecord
from shipments.models import Shipment
from warehouse.models import Warehouse, InventoryItem
from transport.models import Route, Schedule
from bookings.models import Booking


@login_required
def home_dashboard(request):
    # Fleet KPIs
    total_vehicles = Vehicle.objects.count()
    available_vehicles = Vehicle.objects.filter(status=Vehicle.Status.AVAILABLE).count()
    on_trip_vehicles = Vehicle.objects.filter(status=Vehicle.Status.ON_TRIP).count()
    maintenance_vehicles = Vehicle.objects.filter(status=Vehicle.Status.IN_MAINTENANCE).count()

    total_drivers = Driver.objects.count()
    on_duty_drivers = Driver.objects.filter(status=Driver.Status.ON_DUTY).count()

    # Shipment KPIs
    total_shipments = Shipment.objects.count()
    in_transit_shipments = Shipment.objects.filter(current_status=Shipment.Status.IN_TRANSIT).count()
    delivered_shipments = Shipment.objects.filter(current_status=Shipment.Status.DELIVERED).count()
    booked_shipments = Shipment.objects.filter(current_status=Shipment.Status.BOOKED).count()

    # Warehouse KPIs
    total_warehouses = Warehouse.objects.count()
    total_inventory_items = InventoryItem.objects.count()

    # Transport & Bookings
    total_routes = Route.objects.filter(is_active=True).count()
    total_schedules = Schedule.objects.filter(is_active=True).count()
    total_bookings = Booking.objects.count()

    # Recent Records
    recent_shipments = Shipment.objects.select_related('assigned_vehicle', 'assigned_driver').order_by('-created_at')[:5]
    recent_maintenance = MaintenanceRecord.objects.select_related('vehicle').order_by('-service_date')[:5]
    recent_bookings = Booking.objects.select_related('schedule', 'schedule__route').order_by('-booking_date')[:5]

    context = {
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'on_trip_vehicles': on_trip_vehicles,
        'maintenance_vehicles': maintenance_vehicles,
        'total_drivers': total_drivers,
        'on_duty_drivers': on_duty_drivers,
        'total_shipments': total_shipments,
        'in_transit_shipments': in_transit_shipments,
        'delivered_shipments': delivered_shipments,
        'booked_shipments': booked_shipments,
        'total_warehouses': total_warehouses,
        'total_inventory_items': total_inventory_items,
        'total_routes': total_routes,
        'total_schedules': total_schedules,
        'total_bookings': total_bookings,
        'recent_shipments': recent_shipments,
        'recent_maintenance': recent_maintenance,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'dashboard/home.html', context)
