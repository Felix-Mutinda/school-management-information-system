from django.urls import path

from . import views as sm_views


app_name = 'settings_module'
urlpatterns = [
    path('', sm_views.HomeView.as_view(), name='home'),

    # settings for subjects
    path('add_subject/', sm_views.AddSubjectView.as_view(), name='add_subject'),
    path('subject/<int:subject_id>/delete/', sm_views.delete_subject, name='delete_subject'),

    # settings for grading system
    path('add_grading_system/', sm_views.AddGradingSystemView.as_view(), name='add_grading_system'),
    path('grading_system/<int:grading_system_id>/delete/', sm_views.delete_grading_system, name='delete_grading_system'),
]