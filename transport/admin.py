from django.contrib import admin
from .models import Route, Schedule


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('route_code', 'source_city', 'destination_city', 'distance_km', 'estimated_duration_hours', 'is_active')
    list_filter = ('is_active', 'source_city', 'destination_city')
    search_fields = ('route_code', 'source_city', 'destination_city')
    inlines = [ScheduleInline]


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('route', 'vehicle', 'departure_time', 'arrival_time', 'fare', 'available_seats', 'frequency')
    list_filter = ('frequency', 'is_active')
