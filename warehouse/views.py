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
