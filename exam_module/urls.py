from django.urls import path

from . import views

app_name = 'exam_module'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('create/one/', views.CreateOneExamView.as_view(), name='create_one_exam'),
    path('create/many/filter/', views.CreateManyExamsFilterView.as_view(), name='create_many_exams_filter'),
    path('create/many/', views.CreateManyExamsView.as_view(), name='create_many_exams'),
    path('reports/', views.ExamReportsView.as_view(), name='exam_reports_home'),
    path('reports/generate/', views.GenerateExamReportsView.as_view(), name='generate_exam_reports'),
] 