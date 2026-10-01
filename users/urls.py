from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('manage/', views.user_list, name='user_list'),
    path('manage/<int:pk>/role/', views.user_role_update, name='user_role_update'),
]
