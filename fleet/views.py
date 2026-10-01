import json
import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicle, Driver, MaintenanceRecord
from warehouse.models import Warehouse


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
