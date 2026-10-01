import csv
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Shipment, ShipmentStatusHistory
from fleet.models import Vehicle, Driver
from warehouse.models import Warehouse


def get_shipment_progress(status):
    stages = ['BOOKED', 'PICKED_UP', 'AT_HUB', 'IN_TRANSIT', 'OUT_FOR_DELIVERY', 'DELIVERED']
    if status in stages:
        idx = stages.index(status)
        pct = int(((idx + 1) / len(stages)) * 100)
        return pct, stages[:idx + 1]
    return 15, ['BOOKED']


@login_required
def shipment_list(request):
    status_filter = request.GET.get('status')
    shipments = Shipment.objects.select_related(
        'assigned_vehicle', 'assigned_driver', 'origin_warehouse', 'destination_warehouse'
    ).all().order_by('-created_at')

    if status_filter:
        shipments = shipments.filter(current_status=status_filter)

    return render(request, 'shipments/shipment_list.html', {
        'shipments': shipments,
        'status_choices': Shipment.Status.choices,
        'selected_status': status_filter,
    })


@login_required
def shipment_detail(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    timeline = shipment.timeline.all().order_by('-timestamp')
    progress_pct, completed_stages = get_shipment_progress(shipment.current_status)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        location_checkpoint = request.POST.get('location_checkpoint')
        notes = request.POST.get('notes')

        shipment.current_status = new_status
        if new_status == Shipment.Status.DELIVERED:
            shipment.delivered_at = timezone.now()
        shipment.save()

        ShipmentStatusHistory.objects.create(
            shipment=shipment,
            status=new_status,
            location_checkpoint=location_checkpoint,
            notes=notes,
            updated_by=request.user
        )
        messages.success(request, f"Shipment status updated to {new_status}.")
        return redirect('shipments:shipment_detail', pk=shipment.pk)

    return render(request, 'shipments/shipment_detail.html', {
        'shipment': shipment,
        'timeline': timeline,
        'status_choices': Shipment.Status.choices,
        'progress_pct': progress_pct,
        'completed_stages': completed_stages,
    })


@login_required
def shipment_create(request):
    if request.method == 'POST':
        sender_name = request.POST.get('sender_name')
        sender_phone = request.POST.get('sender_phone')
        sender_address = request.POST.get('sender_address')
        receiver_name = request.POST.get('receiver_name')
        receiver_phone = request.POST.get('receiver_phone')
        receiver_address = request.POST.get('receiver_address')
        weight_kg = request.POST.get('weight_kg')
        description = request.POST.get('description')
        shipping_cost = request.POST.get('shipping_cost') or 0.00
        origin_wh_id = request.POST.get('origin_warehouse')
        dest_wh_id = request.POST.get('destination_warehouse')
        vehicle_id = request.POST.get('assigned_vehicle')
        driver_id = request.POST.get('assigned_driver')

        origin_wh = Warehouse.objects.filter(pk=origin_wh_id).first() if origin_wh_id else None
        dest_wh = Warehouse.objects.filter(pk=dest_wh_id).first() if dest_wh_id else None
        vehicle = Vehicle.objects.filter(pk=vehicle_id).first() if vehicle_id else None
        driver = Driver.objects.filter(pk=driver_id).first() if driver_id else None

        shipment = Shipment.objects.create(
            sender_name=sender_name,
            sender_phone=sender_phone,
            sender_address=sender_address,
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            receiver_address=receiver_address,
            weight_kg=weight_kg,
            description=description,
            shipping_cost=shipping_cost,
            origin_warehouse=origin_wh,
            destination_warehouse=dest_wh,
            assigned_vehicle=vehicle,
            assigned_driver=driver,
            estimated_delivery=date.today() + timedelta(days=3),
            created_by=request.user
        )

        ShipmentStatusHistory.objects.create(
            shipment=shipment,
            status=Shipment.Status.BOOKED,
            location_checkpoint=origin_wh.city if origin_wh else "Central Logistics Hub",
            notes="Consignment booked and consignment note issued.",
            updated_by=request.user
        )

        messages.success(request, f"Shipment booked successfully with Tracking # {shipment.tracking_number}")
        return redirect('shipments:shipment_detail', pk=shipment.pk)

    warehouses = Warehouse.objects.all()
    vehicles = Vehicle.objects.filter(status=Vehicle.Status.AVAILABLE)
    drivers = Driver.objects.filter(status=Driver.Status.ON_DUTY)
    return render(request, 'shipments/shipment_form.html', {
        'warehouses': warehouses,
        'vehicles': vehicles,
        'drivers': drivers,
    })


@login_required
def shipment_waybill(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    return render(request, 'shipments/waybill.html', {
        'shipment': shipment,
    })


@login_required
def export_shipments_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logicraft_consignments.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Tracking Number', 'Sender Name', 'Sender Phone',
        'Receiver Name', 'Receiver Phone', 'Origin Hub',
        'Destination Hub', 'Weight (kg)', 'Freight Cost (INR)',
        'Status', 'Assigned Vehicle', 'Est Delivery'
    ])

    for s in Shipment.objects.select_related('origin_warehouse', 'destination_warehouse', 'assigned_vehicle').all():
        writer.writerow([
            s.tracking_number, s.sender_name, s.sender_phone,
            s.receiver_name, s.receiver_phone,
            s.origin_warehouse.code if s.origin_warehouse else 'N/A',
            s.destination_warehouse.code if s.destination_warehouse else 'N/A',
            s.weight_kg, s.shipping_cost, s.get_current_status_display(),
            s.assigned_vehicle.reg_number if s.assigned_vehicle else 'Unassigned',
            s.estimated_delivery
        ])

    return response


def track_public(request):
    tracking_number = request.GET.get('tracking_number', '').strip()
    shipment = None
    timeline = []
    progress_pct = 0
    completed_stages = []
    searched = False

    if tracking_number:
        searched = True
        shipment = Shipment.objects.filter(tracking_number__iexact=tracking_number).first()
        if shipment:
            timeline = shipment.timeline.all().order_by('-timestamp')
            progress_pct, completed_stages = get_shipment_progress(shipment.current_status)

    return render(request, 'shipments/track_public.html', {
        'shipment': shipment,
        'timeline': timeline,
        'tracking_number': tracking_number,
        'searched': searched,
        'progress_pct': progress_pct,
        'completed_stages': completed_stages,
    })
