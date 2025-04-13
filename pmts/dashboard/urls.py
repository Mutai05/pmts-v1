from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('all-departments/', views.all_departments, name='all-departments'),
    path('subcounties/', views.subcounties, name='subcounties'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>/', views.single_project, name='single_project'),
    path('feedback/', views.feedback, name='feedback'),
    path('notifications/', views.notifications, name='notifications'),
    path('profile/', views.profile, name='profile'),
]