from rest_framework.serializers import ( ModelSerializer, CharField, FloatField,
                                        EmailField, ChoiceField, ValidationError,
                                        Serializer)
from ..models import Ride, Statuses
from .ride_event import RideEventDetailSerializer

class BaseRideSerializer(ModelSerializer):
    class Meta:
        model = Ride
        fields = [
            'id',
            'status',
            'id_rider',
            'id_driver', 
            'pickup_latitude',
            'pickup_longitude',
            'dropoff_latitude',
            'dropoff_longitude',
            'pickup_time'
        ]

class RideListSerializer(BaseRideSerializer):
    todays_ride_events = RideEventDetailSerializer(many = True, read_only = True)

    class Meta(BaseRideSerializer.Meta):
        fields = BaseRideSerializer.Meta.fields + ['todays_ride_events']

class RideListQueryParamSerializer(Serializer):
    sort_by = CharField(required=False)
    status = ChoiceField(
        choices = Statuses.choices,
        required = False,
        allow_blank = True,
    )
    rider_email = EmailField(required = False, allow_blank = True)
    target_lat = FloatField(
        required = False,
        allow_null = True,
        min_value = -90,
        max_value = 90,
    )
    target_long = FloatField(
        required = False,
        allow_null = True,
        min_value = -180,
        max_value = 180,
    )

    allowed_sort = ['id', 'pickup_time', 'distance']

    def validate_sort_by(self, value):
        sort_key = value.strip('-')
        if sort_key not in self.allowed_sort:
            raise ValidationError(f'Invalid sort: {value}')
        elif sort_key == 'distance':
            missing = [
                name for name in ('target_lat', 'target_long')
                if self.initial_data.get(name) in (None, '')
            ]
            if missing:
                raise ValidationError({
                    name: 'Required when sorting by distance.' for name in missing
                })
        return value