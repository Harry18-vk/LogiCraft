from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('export-csv/', views.export_bookings_csv, name='export_csv'),
    path('book/<int:schedule_id>/', views.book_ticket, name='book_ticket'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
]
