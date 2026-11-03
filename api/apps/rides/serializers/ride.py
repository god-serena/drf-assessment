from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.serializers import ( ModelSerializer, CharField, FloatField,
                                        EmailField, ChoiceField, ValidationError,
                                        Serializer, SerializerMethodField,
                                        DateTimeField, PrimaryKeyRelatedField)
from apps.users.models import Roles
from ..models import Ride, RideEvent, Statuses, ALLOWED_STATUS_TRANSITIONS
from ..services import transition_ride_status
from .ride_event import RideEventDetailSerializer

class BaseRideSerializer(ModelSerializer):
    allowed_next_statuses = SerializerMethodField(read_only=True)
    rider_email = CharField(source='id_rider.email', read_only=True)

    def get_allowed_next_statuses(self, obj):
        return [str(s) for s in ALLOWED_STATUS_TRANSITIONS.get(obj.status, [])]

    class Meta:
        model = Ride
        fields = [
            'id',
            'status',
            'allowed_next_statuses',
            'id_rider',
            'rider_email',
            'id_driver', 
            'pickup_latitude',
            'pickup_longitude',
            'dropoff_latitude',
            'dropoff_longitude',
            'pickup_time'
        ]

class RideDetailSerializer(BaseRideSerializer):
    events = RideEventDetailSerializer(many=True, read_only=True)

    class Meta(BaseRideSerializer.Meta):
        fields = BaseRideSerializer.Meta.fields + ['events']

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

class RideStatusUpdateSerializer(Serializer):
    status = ChoiceField(
        choices=Statuses.choices,
        required=True,
        error_messages={
            'invalid_choice': 'Unknown status "{input}". Allowed values are: '
            + ', '.join(Statuses.values)
            + '.'
        },
    )
    id_driver = PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False,
        allow_null=True,
    )
    pickup_time = DateTimeField(required=False, allow_null=True)
    description = CharField(required=False, allow_blank=True, max_length=255)

    def validate_id_driver(self, value):
        if value is not None and value.role != Roles.DRIVER.value:
            raise ValidationError('Selected user must be a driver.')
        return value

    def validate(self, attrs):
        ride = self.instance
        current_status = ride.status
        next_status = attrs['status']
        allowed_next = ALLOWED_STATUS_TRANSITIONS.get(current_status, [])

        if next_status not in allowed_next:
            if not allowed_next:
                raise ValidationError({
                    'status': f'Ride is in terminal status "{current_status}" and cannot be transitioned further.'
                })
            raise ValidationError({
                'status': f'Cannot change status from {current_status} to {next_status}. Allowed: {", ".join(allowed_next)}.'
            })

        errors = {}
        if next_status == Statuses.PICKED_UP and not attrs.get('pickup_time'):
            errors['pickup_time'] = 'Pickup time is required when picking up the rider.'
        if next_status == Statuses.ASSIGNED and attrs.get('id_driver') is None:
            errors['id_driver'] = 'A driver is required when assigning a ride.'
        if next_status != Statuses.ASSIGNED and 'id_driver' in self.initial_data and attrs.get('id_driver') is not None:
            errors['id_driver'] = 'Driver can only be selected when assigning a ride.'
        if next_status == Statuses.CANCELLED and not (attrs.get('description') or '').strip():
            errors['description'] = 'A cancellation reason is required.'
        if next_status != Statuses.PICKED_UP and 'pickup_time' in self.initial_data and attrs.get('pickup_time') is not None:
            errors['pickup_time'] = 'Pickup time can only be set when picking up the rider.'
        if errors:
            raise ValidationError(errors)

        return attrs

    def update(self, instance, validated_data):
        return transition_ride_status(
            ride=instance,
            next_status=validated_data['status'],
            driver=validated_data.get('id_driver'),
            pickup_time=validated_data.get('pickup_time'),
            description=validated_data.get('description', ''),
        )
