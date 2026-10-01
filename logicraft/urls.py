"""
URL configuration for logicraft project.
P_012: LogiCraft - Logistics & Fleet Management
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('users/', include('users.urls')),
    path('fleet/', include('fleet.urls')),
    path('shipments/', include('shipments.urls')),
    path('warehouse/', include('warehouse.urls')),
    path('transport/', include('transport.urls')),
    path('bookings/', include('bookings.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
