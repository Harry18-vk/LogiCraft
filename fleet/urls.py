from django.urls import path
from . import views

app_name = 'fleet'

urlpatterns = [
    path('', views.fleet_list, name='fleet_list'),
    path('map/', views.fleet_map_view, name='fleet_map'),
    path('export-csv/', views.export_fleet_csv, name='export_csv'),
    path('vehicle/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicle/add/', views.vehicle_create, name='vehicle_create'),
]
