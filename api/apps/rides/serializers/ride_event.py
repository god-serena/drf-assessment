from django.utils import timezone
from rest_framework.serializers import (
    CharField,
    DateTimeField,
    EmailField,
    ModelSerializer,
    Serializer,
    ValidationError,
)

from ..models import RideEvent, RideEventCorrection
from ..services import correct_ride_event


class RideEventCorrectionSerializer(ModelSerializer):
    corrected_by_email = EmailField(source='corrected_by.email', read_only=True)

    class Meta:
        model = RideEventCorrection
        fields = [
            'id',
            'corrected_by_email',
            'previous_occurred_at',
            'new_occurred_at',
            'reason',
            'created_at',
        ]


class BaseRideEventSerializer(ModelSerializer):
    effective_time = DateTimeField(read_only=True)
    corrections = RideEventCorrectionSerializer(many=True, read_only=True)

    class Meta:
        model = RideEvent
        fields = [
            'id',
            'ride',
            'description',
            'created_at',
            'occurred_at',
            'effective_time',
            'corrections',
        ]


class RideEventDetailSerializer(BaseRideEventSerializer):
    pass


class RideEventCorrectionInputSerializer(Serializer):
    occurred_at = DateTimeField(required=True)
    reason = CharField(required=True, min_length=3, max_length=255)

    def validate_occurred_at(self, value):
        if value > timezone.now():
            raise ValidationError('Timestamp cannot be in the future.')
        return value

    def validate(self, attrs):
        event = self.context['event']
        new_time = attrs['occurred_at']
        reason = (attrs.get('reason') or '').strip()
        if not reason:
            raise ValidationError({'reason': 'Please provide a reason for the correction.'})

        events = list(event.ride.events.order_by('created_at', 'id'))
        try:
            idx = [e.pk for e in events].index(event.pk)
        except ValueError:
            idx = -1

        if idx > 0:
            prev_event = events[idx - 1]
            if new_time < prev_event.effective_time:
                raise ValidationError({
                    'occurred_at': 'Timestamp cannot be earlier than previous event.'
                })

        if idx != -1 and idx < len(events) - 1:
            next_event = events[idx + 1]
            if new_time > next_event.effective_time:
                raise ValidationError({
                    'occurred_at': 'Timestamp cannot be later than subsequent event.'
                })

        attrs['reason'] = reason
        return attrs

    def save(self, **kwargs):
        event = self.context['event']
        user = self.context['request'].user
        return correct_ride_event(
            event=event,
            new_occurred_at=self.validated_data['occurred_at'],
            reason=self.validated_data['reason'],
            user=user,
        )
