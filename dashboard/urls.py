from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('executive-dashboard/', views.executive_dashboard, name='executive_dashboard'),
    path('departmental-dashboard/', views.departmental_dashboard, name='departmental_dashboard'),
    path('public-dashboard/', views.public_dashboard, name='public_dashboard'),
]