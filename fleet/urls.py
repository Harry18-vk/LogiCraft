from django.urls import path
from . import views

app_name = 'fleet'

urlpatterns = [
    path('', views.fleet_list, name='fleet_list'),
    path('map/', views.fleet_map_view, name='fleet_map'),
    path('export-csv/', views.export_fleet_csv, name='export_csv'),
    path('vehicle/add/', views.vehicle_create, name='vehicle_create'),
    path('vehicle/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicle/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicle/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('vehicle/<int:vehicle_pk>/maintenance/add/', views.maintenance_create, name='maintenance_create'),
    path('maintenance/<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),
]
