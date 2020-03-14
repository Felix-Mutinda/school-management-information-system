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

    # settings for exam types
    path('add_exam_type/', sm_views.AddExamTypeView.as_view(), name='add_exam_type'),
    path('exam_type/<int:exam_type_id>/delete/', sm_views.delete_exam_type, name='delete_exam_type'),

    # settings for terms
    path('add_term/', sm_views.AddTermView.as_view(), name='add_term'),
    path('term/<int:term_id>/delete/', sm_views.delete_term, name='delete_term'),

    # settings for streams
    path('add_stream/', sm_views.AddStreamView.as_view(), name='add_stream'),
    path('stream/<int:stream_id>/delete/', sm_views.delete_stream, name='delete_stream'),


]