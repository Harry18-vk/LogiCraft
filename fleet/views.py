import json
import csv
from datetime import date
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicle, Driver, MaintenanceRecord
from warehouse.models import Warehouse
from shipments.models import Shipment, ShipmentStatusHistory


@login_required
def fleet_list(request):
    vehicles = Vehicle.objects.all().order_by('-created_at')
    drivers = Driver.objects.select_related('user', 'assigned_vehicle').all()
    maintenance_records = MaintenanceRecord.objects.select_related('vehicle').order_by('-service_date')[:10]
    return render(request, 'fleet/fleet_list.html', {
        'vehicles': vehicles,
        'drivers': drivers,
        'maintenance_records': maintenance_records,
    })


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    maintenance_logs = vehicle.maintenance_logs.all().order_by('-service_date')
    shipments = vehicle.shipments.all().order_by('-created_at')[:5]
    return render(request, 'fleet/vehicle_detail.html', {
        'vehicle': vehicle,
        'maintenance_logs': maintenance_logs,
        'shipments': shipments,
    })


@login_required
def vehicle_create(request):
    if request.method == 'POST':
        reg_number = request.POST.get('reg_number')
        model_name = request.POST.get('model_name')
        vehicle_type = request.POST.get('vehicle_type')
        capacity_kg = request.POST.get('capacity_kg')
        passenger_capacity = request.POST.get('passenger_capacity', 0)
        fuel_type = request.POST.get('fuel_type')
        current_location = request.POST.get('current_location')

        if Vehicle.objects.filter(reg_number=reg_number).exists():
            messages.error(request, f"Vehicle with registration '{reg_number}' already exists.")
            return redirect('fleet:vehicle_create')

        Vehicle.objects.create(
            reg_number=reg_number,
            model_name=model_name,
            vehicle_type=vehicle_type,
            capacity_kg=capacity_kg,
            passenger_capacity=passenger_capacity or 0,
            fuel_type=fuel_type,
            current_location=current_location,
            status=Vehicle.Status.AVAILABLE
        )
        messages.success(request, f"Vehicle {reg_number} successfully registered in fleet.")
        return redirect('fleet:fleet_list')

    return render(request, 'fleet/vehicle_form.html', {
        'vehicle_types': Vehicle.VehicleType.choices,
        'fuel_types': Vehicle.FuelType.choices,
        'action': 'Register',
    })


@login_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.model_name = request.POST.get('model_name')
        vehicle.vehicle_type = request.POST.get('vehicle_type')
        vehicle.capacity_kg = request.POST.get('capacity_kg')
        vehicle.passenger_capacity = request.POST.get('passenger_capacity', 0) or 0
        vehicle.fuel_type = request.POST.get('fuel_type')
        vehicle.current_location = request.POST.get('current_location')
        vehicle.status = request.POST.get('status')
        vehicle.odometer_km = request.POST.get('odometer_km', 0) or 0
        vehicle.latitude = request.POST.get('latitude') or 28.6139
        vehicle.longitude = request.POST.get('longitude') or 77.2090
        vehicle.save()
        messages.success(request, f"Vehicle {vehicle.reg_number} updated successfully.")
        return redirect('fleet:vehicle_detail', pk=vehicle.pk)

    return render(request, 'fleet/vehicle_form.html', {
        'vehicle': vehicle,
        'vehicle_types': Vehicle.VehicleType.choices,
        'fuel_types': Vehicle.FuelType.choices,
        'status_choices': Vehicle.Status.choices,
        'action': 'Edit',
    })


@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        reg = vehicle.reg_number
        vehicle.delete()
        messages.success(request, f"Vehicle {reg} removed from fleet.")
        return redirect('fleet:fleet_list')
    return render(request, 'fleet/vehicle_confirm_delete.html', {'vehicle': vehicle})


@login_required
def maintenance_create(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        description = request.POST.get('description')
        service_date = request.POST.get('service_date')
        cost = request.POST.get('cost', 0.00)
        odometer_at_service = request.POST.get('odometer_at_service', 0)
        status = request.POST.get('status', MaintenanceRecord.Status.COMPLETED)
        notes = request.POST.get('notes', '')

        MaintenanceRecord.objects.create(
            vehicle=vehicle,
            service_type=service_type,
            description=description,
            service_date=service_date,
            cost=cost,
            odometer_at_service=odometer_at_service,
            status=status,
            notes=notes,
        )
        messages.success(request, f"Maintenance record added for {vehicle.reg_number}.")
        return redirect('fleet:vehicle_detail', pk=vehicle.pk)

    return render(request, 'fleet/maintenance_form.html', {
        'vehicle': vehicle,
        'service_types': MaintenanceRecord.ServiceType.choices,
        'status_choices': MaintenanceRecord.Status.choices,
    })


@login_required
def maintenance_delete(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk)
    vehicle_pk = record.vehicle.pk
    if request.method == 'POST':
        record.delete()
        messages.success(request, "Maintenance record deleted.")
        return redirect('fleet:vehicle_detail', pk=vehicle_pk)
    return render(request, 'fleet/maintenance_confirm_delete.html', {'record': record})


@login_required
def fleet_map_view(request):
    vehicles = Vehicle.objects.all()
    warehouses = Warehouse.objects.all()

    vehicles_data = [
        {
            'id': v.id,
            'reg_number': v.reg_number,
            'model': v.model_name,
            'type': v.get_vehicle_type_display(),
            'status': v.status,
            'status_display': v.get_status_display(),
            'location': v.current_location or "En Route",
            'lat': float(v.latitude or 28.6139),
            'lng': float(v.longitude or 77.2090),
        }
        for v in vehicles
    ]

    warehouses_data = [
        {
            'id': w.id,
            'code': w.code,
            'name': w.name,
            'city': w.city,
            'capacity': str(w.total_capacity_sqft),
            'lat': float(w.latitude or 28.6139),
            'lng': float(w.longitude or 77.2090),
        }
        for w in warehouses
    ]

    return render(request, 'fleet/fleet_map.html', {
        'vehicles_json': json.dumps(vehicles_data),
        'warehouses_json': json.dumps(warehouses_data),
        'vehicles_count': vehicles.count(),
        'warehouses_count': warehouses.count(),
    })


@login_required
def export_fleet_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logicraft_fleet_assets.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Reg Number', 'Model', 'Category', 'Capacity (kg)',
        'Passengers', 'Fuel', 'Odometer (km)', 'Status', 'Current Location'
    ])

    for v in Vehicle.objects.all():
        writer.writerow([
            v.reg_number, v.model_name, v.get_vehicle_type_display(),
            v.capacity_kg, v.passenger_capacity, v.get_fuel_type_display(),
            v.odometer_km, v.get_status_display(), v.current_location
        ])

    return response


@login_required
def driver_portal(request):
    driver = getattr(request.user, 'driver_profile', None)
    if not driver and not request.user.is_superuser:
        messages.error(request, "Access restricted to fleet drivers.")
        return redirect('dashboard:home')

    # If superuser testing without driver profile, view first driver
    if not driver and request.user.is_superuser:
        driver = Driver.objects.first()

    assigned_vehicle = driver.assigned_vehicle if driver else None

    active_shipments = []
    completed_shipments = []
    if driver:
        active_shipments = Shipment.objects.filter(
            assigned_driver=driver
        ).exclude(
            current_status=Shipment.Status.DELIVERED
        ).select_related('origin_warehouse', 'destination_warehouse', 'assigned_vehicle').order_by('-created_at')

        completed_shipments = Shipment.objects.filter(
            assigned_driver=driver,
            current_status=Shipment.Status.DELIVERED
        ).select_related('origin_warehouse', 'destination_warehouse').order_by('-delivered_at')[:5]

    return render(request, 'fleet/driver_portal.html', {
        'driver': driver,
        'vehicle': assigned_vehicle,
        'active_shipments': active_shipments,
        'completed_shipments': completed_shipments,
        'status_choices': Shipment.Status.choices,
    })


@login_required
def driver_update_shipment(request, pk):
    driver = getattr(request.user, 'driver_profile', None)
    if not driver and not request.user.is_superuser:
        messages.error(request, "Unauthorized action.")
        return redirect('fleet:driver_portal')

    shipment = get_object_or_404(Shipment, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        checkpoint = request.POST.get('location_checkpoint', '').strip()
        notes = request.POST.get('notes', '').strip()

        if new_status:
            shipment.current_status = new_status
            if new_status == Shipment.Status.DELIVERED:
                shipment.delivered_at = timezone.now()
                if driver:
                    driver.status = Driver.Status.ON_DUTY
                    driver.save()
                if shipment.assigned_vehicle:
                    shipment.assigned_vehicle.status = Vehicle.Status.AVAILABLE
                    shipment.assigned_vehicle.save()
            elif new_status == Shipment.Status.IN_TRANSIT:
                if driver:
                    driver.status = Driver.Status.ON_TRIP
                    driver.save()
                if shipment.assigned_vehicle:
                    shipment.assigned_vehicle.status = Vehicle.Status.ON_TRIP
                    shipment.assigned_vehicle.save()

            shipment.save()

            if checkpoint and shipment.assigned_vehicle:
                shipment.assigned_vehicle.current_location = checkpoint
                shipment.assigned_vehicle.save()

            ShipmentStatusHistory.objects.create(
                shipment=shipment,
                status=new_status,
                location_checkpoint=checkpoint or (shipment.assigned_vehicle.current_location if shipment.assigned_vehicle else "En Route"),
                notes=notes or f"Status logged by driver {request.user.get_full_name() or request.user.username}",
                updated_by=request.user
            )
            messages.success(request, f"Shipment {shipment.tracking_number} status updated to {shipment.get_current_status_display()}!")

    return redirect('fleet:driver_portal')


@login_required
def driver_toggle_duty(request):
    driver = getattr(request.user, 'driver_profile', None)
    if not driver:
        messages.error(request, "Driver profile not found.")
        return redirect('fleet:driver_portal')

    if request.method == 'POST':
        new_status = request.POST.get('duty_status')
        if new_status in [Driver.Status.ON_DUTY, Driver.Status.OFF_DUTY, Driver.Status.ON_LEAVE]:
            driver.status = new_status
            driver.save()
            messages.success(request, f"Duty status updated to {driver.get_status_display()}.")

    return redirect('fleet:driver_portal')


@login_required
def driver_report_issue(request):
    driver = getattr(request.user, 'driver_profile', None)
    if not driver or not driver.assigned_vehicle:
        messages.error(request, "No vehicle assigned to report issue for.")
        return redirect('fleet:driver_portal')

    if request.method == 'POST':
        service_type = request.POST.get('service_type', MaintenanceRecord.ServiceType.EMERGENCY)
        description = request.POST.get('description', '').strip()
        odometer = request.POST.get('odometer', driver.assigned_vehicle.odometer_km)

        if description:
            MaintenanceRecord.objects.create(
                vehicle=driver.assigned_vehicle,
                service_type=service_type,
                description=f"[Reported by Driver {request.user.username}]: {description}",
                service_date=date.today(),
                odometer_at_service=odometer or driver.assigned_vehicle.odometer_km,
                status=MaintenanceRecord.Status.SCHEDULED,
                notes="Driver flagged incident from driver portal."
            )
            driver.assigned_vehicle.status = Vehicle.Status.IN_MAINTENANCE
            driver.assigned_vehicle.save()
            messages.warning(request, f"Incident reported for {driver.assigned_vehicle.reg_number}. Maintenance scheduled!")

    return redirect('fleet:driver_portal')

