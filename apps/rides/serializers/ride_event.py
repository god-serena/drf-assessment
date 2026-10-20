from rest_framework import serializers
from ..models import RideEvent


class BaseRideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = [
            'id',
            'ride',
            'description',
            'created_at'
        ]
        
class RideEventDetailSerializer(BaseRideEventSerializer):
    pass