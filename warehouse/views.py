from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Warehouse, InventoryItem


@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.prefetch_related('inventory_items').all()
    return render(request, 'warehouse/warehouse_list.html', {
        'warehouses': warehouses,
    })


@login_required
def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    items = warehouse.inventory_items.all()

    if request.method == 'POST':
        sku = request.POST.get('sku')
        item_name = request.POST.get('item_name')
        category = request.POST.get('category')
        quantity = request.POST.get('quantity')
        unit_weight_kg = request.POST.get('unit_weight_kg')

        InventoryItem.objects.update_or_create(
            warehouse=warehouse,
            sku=sku,
            defaults={
                'item_name': item_name,
                'category': category,
                'quantity': quantity,
                'unit_weight_kg': unit_weight_kg,
            }
        )
        messages.success(request, f"Item {sku} updated/added to {warehouse.code}.")
        return redirect('warehouse:warehouse_detail', pk=warehouse.pk)

    return render(request, 'warehouse/warehouse_detail.html', {
        'warehouse': warehouse,
        'items': items,
        'categories': InventoryItem.Category.choices,
    })


@login_required
def warehouse_create(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        name = request.POST.get('name', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        address = request.POST.get('address', '').strip()
        total_capacity_sqft = request.POST.get('total_capacity_sqft', 50000)
        manager_name = request.POST.get('manager_name', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        latitude = request.POST.get('latitude') or 28.6139
        longitude = request.POST.get('longitude') or 77.2090

        if Warehouse.objects.filter(code=code).exists():
            messages.error(request, f"Warehouse code '{code}' already exists.")
            return redirect('warehouse:warehouse_create')

        warehouse = Warehouse.objects.create(
            code=code,
            name=name,
            city=city,
            state=state,
            address=address,
            total_capacity_sqft=total_capacity_sqft,
            manager_name=manager_name,
            contact_phone=contact_phone,
            latitude=latitude,
            longitude=longitude,
        )
        messages.success(request, f"Warehouse {code} - {name} created successfully.")
        return redirect('warehouse:warehouse_detail', pk=warehouse.pk)

    return render(request, 'warehouse/warehouse_form.html', {
        'status_choices': Warehouse.Status.choices,
        'action': 'Create',
    })


@login_required
def warehouse_edit(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        warehouse.name = request.POST.get('name', '').strip()
        warehouse.city = request.POST.get('city', '').strip()
        warehouse.state = request.POST.get('state', '').strip()
        warehouse.address = request.POST.get('address', '').strip()
        warehouse.total_capacity_sqft = request.POST.get('total_capacity_sqft', 50000)
        warehouse.manager_name = request.POST.get('manager_name', '').strip()
        warehouse.contact_phone = request.POST.get('contact_phone', '').strip()
        warehouse.status = request.POST.get('status')
        warehouse.latitude = request.POST.get('latitude') or 28.6139
        warehouse.longitude = request.POST.get('longitude') or 77.2090
        warehouse.save()
        messages.success(request, f"Warehouse {warehouse.code} updated successfully.")
        return redirect('warehouse:warehouse_detail', pk=warehouse.pk)

    return render(request, 'warehouse/warehouse_form.html', {
        'warehouse': warehouse,
        'status_choices': Warehouse.Status.choices,
        'action': 'Edit',
    })


@login_required
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        code = warehouse.code
        warehouse.delete()
        messages.success(request, f"Warehouse {code} deleted successfully.")
        return redirect('warehouse:warehouse_list')
    return render(request, 'warehouse/warehouse_confirm_delete.html', {'warehouse': warehouse})


@login_required
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    warehouse_pk = item.warehouse.pk
    if request.method == 'POST':
        sku = item.sku
        item.delete()
        messages.success(request, f"Item {sku} removed from warehouse.")
        return redirect('warehouse:warehouse_detail', pk=warehouse_pk)
    return render(request, 'warehouse/inventory_confirm_delete.html', {'item': item})
