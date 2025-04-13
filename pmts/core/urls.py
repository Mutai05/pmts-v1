from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('all-financial-years/', views.all_financial_years, name='all_financial_years'),
    path('fy-2022-2023/', views.fy_2022_2023, name='fy_2022_2023'),
    path('fy-2023-2024/', views.fy_2023_2024, name='fy_2023_2024'),
    path('fy-2024-2025/', views.fy_2024_2025, name='fy_2024_2025'),
    path('fy-2025-2026/', views.fy_2025_2026, name='fy_2025_2026'),
    path('fy-2026-2027/', views.fy_2026_2027, name='fy_2026_2027'),
    path('departments/', views.departments, name='departments'),
    path('gallery/', views.gallery, name='gallery'),
    path('resources/', views.resources, name='resources'),
    path('faqs/', views.faqs, name='faqs'),
    path('contacts/', views.contact, name='contacts'),
]