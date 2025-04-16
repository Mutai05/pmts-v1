from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('export/excel/', views.export_projects_excel, name='export_projects_excel'),
    path('create/', views.project_create, name='project_create'),
    path('feedback-dashboard/', views.feedback_dashboard, name='feedback_dashboard'),
    path('<slug:slug>/', views.project_detail, name='project_detail'),
    path('<slug:slug>/update/', views.project_update, name='project_update'),
    path('<slug:slug>/progress/', views.project_progress_update, name='project_progress'),
    path('<slug:slug>/feedback/', views.project_feedback, name='project_feedback'),
    path('<slug:slug>/photos/', views.project_manage_photos, name='project_manage_photos'),
]