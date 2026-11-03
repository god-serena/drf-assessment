from django.db import transaction
from django.utils import timezone

from .models import (
    ALLOWED_STATUS_TRANSITIONS,
    Ride,
    RideEvent,
    RideEventCorrection,
    Statuses,
)


DEFAULT_STATUS_EVENT_DESCRIPTIONS = {
    Statuses.REQUESTED: 'Ride requested',
    Statuses.ASSIGNED: 'Driver assigned',
    Statuses.ENROUTE: 'Driver en route to pickup',
    Statuses.PICKED_UP: 'Rider picked up',
    Statuses.COMPLETED: 'Ride completed',
    Statuses.CANCELLED: 'Ride cancelled',
}


def format_event_description(status, ride, description=''):
    if description and description.strip():
        return description.strip()
    if status == Statuses.ASSIGNED and getattr(ride, 'id_driver', None):
        return f'Driver assigned: {ride.id_driver.email}'
    return DEFAULT_STATUS_EVENT_DESCRIPTIONS.get(status, f'Status changed to {status}')


def transition_ride_status(ride, next_status, driver=None, pickup_time=None, description=''):
    with transaction.atomic():
        locked_ride = Ride.objects.select_for_update().get(pk=ride.pk)
        allowed_next = ALLOWED_STATUS_TRANSITIONS.get(locked_ride.status, [])
        if next_status not in allowed_next:
            raise ValueError(
                f'Cannot transition ride from {locked_ride.status} to {next_status}'
            )

        update_fields = ['status']
        locked_ride.status = next_status

        if next_status == Statuses.ASSIGNED and driver is not None:
            locked_ride.id_driver = driver
            update_fields.append('id_driver')

        if next_status == Statuses.PICKED_UP and pickup_time is not None:
            locked_ride.pickup_time = pickup_time
            update_fields.append('pickup_time')

        locked_ride.save(update_fields=update_fields)

        event_description = format_event_description(next_status, locked_ride, description)
        event_time = (
            pickup_time
            if next_status == Statuses.PICKED_UP and pickup_time
            else timezone.now()
        )
        RideEvent.objects.create(
            ride=locked_ride,
            description=event_description,
            occurred_at=event_time,
        )

    return locked_ride


def correct_ride_event(event, new_occurred_at, reason, user):
    with transaction.atomic():
        previous_occurred_at = event.effective_time
        event.occurred_at = new_occurred_at
        event.save(update_fields=['occurred_at'])

        RideEventCorrection.objects.create(
            event=event,
            corrected_by=user,
            previous_occurred_at=previous_occurred_at,
            new_occurred_at=new_occurred_at,
            reason=reason.strip(),
        )

        if 'picked up' in event.description.lower() and event.ride.pickup_time:
            event.ride.pickup_time = new_occurred_at
            event.ride.save(update_fields=['pickup_time'])

    return event
