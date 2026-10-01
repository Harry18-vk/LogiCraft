from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Route, Schedule


@login_required
def route_list(request):
    routes = Route.objects.prefetch_related('schedules', 'schedules__vehicle').filter(is_active=True)
    return render(request, 'transport/route_list.html', {
        'routes': routes,
    })
