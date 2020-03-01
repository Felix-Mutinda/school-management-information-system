from django.urls import path

from . import views as sm_views


app_name = 'settings_module'
urlpatterns = [
    path('', sm_views.HomeView.as_view(), name='home'),

    # settings for subjects
    path('add_subject/', sm_views.AddSubjectView.as_view(), name='add_subject'),
    path('subject/<int:subject_id>/delete/', sm_views.delete_subject, name='delete_subject'),
]