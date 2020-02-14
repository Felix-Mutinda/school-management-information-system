from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.home, name='home'),

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
]