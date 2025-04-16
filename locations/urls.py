from django.urls import path
from .views import WardListAPIView

app_name = 'locations'

urlpatterns = [
    path('api/wards/', WardListAPIView.as_view(), name='api_ward_list'),
    # Add other locations URLs here if needed
]