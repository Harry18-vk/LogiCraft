from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.warehouse_list, name='warehouse_list'),
    path('add/', views.warehouse_create, name='warehouse_create'),
    path('<int:pk>/', views.warehouse_detail, name='warehouse_detail'),
    path('<int:pk>/edit/', views.warehouse_edit, name='warehouse_edit'),
    path('<int:pk>/delete/', views.warehouse_delete, name='warehouse_delete'),
    path('inventory/<int:pk>/delete/', views.inventory_delete, name='inventory_delete'),
]
