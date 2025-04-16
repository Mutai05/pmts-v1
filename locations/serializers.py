from rest_framework import serializers
from .models import Ward


class WardSerializer(serializers.ModelSerializer):
    """
    Serializer for the Ward model.
    """
    class Meta:
        model = Ward
        fields = ['id', 'name']