from django.urls import path
from django.contrib.auth import views as auth_views

from . import views as accounts_views

app_name = 'accounts'
urlpatterns = [
    path('', accounts_views.HomeView.as_view(), name='home'),

    path('login/', accounts_views.StaffLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/staff/', accounts_views.register_staff, name='register_staff'),
    path('staff/', accounts_views.ListStaffView.as_view(), name='list_staff'),
    path('register/student/', accounts_views.RegisterStudentView.as_view(), name='register_student'),
]