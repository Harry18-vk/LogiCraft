from django.urls import path
from . import views

app_name = 'shipments'

urlpatterns = [
    path('', views.shipment_list, name='shipment_list'),
    path('new/', views.shipment_create, name='shipment_create'),
    path('track/', views.track_public, name='track_public'),
    path('export-csv/', views.export_shipments_csv, name='export_csv'),
    path('<int:pk>/', views.shipment_detail, name='shipment_detail'),
    path('<int:pk>/waybill/', views.shipment_waybill, name='shipment_waybill'),
]
