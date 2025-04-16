from django.shortcuts import render
from rest_framework.generics import ListAPIView

from .models import Ward
from .serializers import WardSerializer

# Create your views here.

class WardListAPIView(ListAPIView):
    """
    API view to list wards, optionally filtered by subcounty.
    Expects a 'subcounty' query parameter containing the SubCounty ID.
    """
    serializer_class = WardSerializer
    # queryset = Ward.objects.all() # We will override get_queryset

    def get_queryset(self):
        """ Optionally filter wards by subcounty ID provided in query params. """
        queryset = Ward.objects.all().order_by('name')
        subcounty_id = self.request.query_params.get('subcounty', None)

        if subcounty_id is not None:
            # Ensure subcounty_id is a valid integer before filtering
            try:
                subcounty_id = int(subcounty_id)
                queryset = queryset.filter(subcounty_id=subcounty_id)
            except ValueError:
                # Handle invalid subcounty_id (e.g., return empty list or raise error)
                # For simplicity, we return an empty queryset if the ID is invalid
                queryset = Ward.objects.none()

        return queryset
