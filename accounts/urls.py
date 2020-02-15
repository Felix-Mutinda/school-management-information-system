from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.home, name='home'),

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('accounts/register/staff/', views.register_staff, name='register_staff'),
    path('accounts/staff/', views.ListStaffView.as_view(), name='list_staff'),
]