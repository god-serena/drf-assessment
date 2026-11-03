from django.db.models import (TextChoices, CharField, Model, ForeignKey, Q,
                              PROTECT, FloatField, DateTimeField, CheckConstraint)
from django.conf import settings

# Create your models here.
class Statuses(TextChoices):
    ASSIGNED = 'ASSIGNED', 'Assigned'
    CANCELLED = 'CANCELLED', 'Cancelled'
    COMPLETED = 'COMPLETED', 'Completed'
    ENROUTE = 'ENROUTE', 'Enroute'
    PICKED_UP = 'PICKED_UP', 'Picked up'
    REQUESTED = 'REQUESTED', 'Requested'
    SCHEDULED = 'SCHEDULED', 'Scheduled'

ALLOWED_STATUS_TRANSITIONS = {
    Statuses.REQUESTED: [Statuses.ASSIGNED, Statuses.CANCELLED],
    Statuses.SCHEDULED: [Statuses.ASSIGNED, Statuses.CANCELLED],
    Statuses.ASSIGNED: [Statuses.ENROUTE, Statuses.CANCELLED],
    Statuses.ENROUTE: [Statuses.PICKED_UP, Statuses.CANCELLED],
    Statuses.PICKED_UP: [Statuses.COMPLETED, Statuses.CANCELLED],
    Statuses.COMPLETED: [],
    Statuses.CANCELLED: [],
}

class Ride(Model):
    status = CharField(
        max_length = 15,
        choices = Statuses.choices,
        default = Statuses.REQUESTED,
        db_default = Statuses.REQUESTED
    )
    id_rider = ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'rider_rides',
        on_delete = PROTECT
    )
    id_driver = ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'drive_rides',
        on_delete = PROTECT,
        null=True,
        blank=True
    )
    pickup_latitude = FloatField()
    pickup_longitude = FloatField()
    dropoff_latitude = FloatField()
    dropoff_longitude = FloatField()
    pickup_time = DateTimeField()
    
    class Meta:
        constraints = [
            CheckConstraint(
                check = Q(status__in = Statuses.values),
                name = 'status_constraint'
            )
        ]