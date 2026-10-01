from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    path('', views.route_list, name='route_list'),
    path('route/add/', views.route_create, name='route_create'),
    path('route/<int:pk>/edit/', views.route_edit, name='route_edit'),
    path('route/<int:pk>/delete/', views.route_delete, name='route_delete'),
    path('route/<int:route_pk>/schedule/add/', views.schedule_create, name='schedule_create'),
    path('schedule/<int:pk>/edit/', views.schedule_edit, name='schedule_edit'),
    path('schedule/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),
]
