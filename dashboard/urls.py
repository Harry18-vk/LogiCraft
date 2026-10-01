from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_dashboard, name='home'),
]
