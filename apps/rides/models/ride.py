from django.db.models import (TextChoices, CharField, Model, ForeignKey, Q,
                              PROTECT, FloatField, DateTimeField, CheckConstraint)
from django.conf import settings

# Create your models here.
class Statuses(TextChoices):
    ASSIGNED = 'ASSIGNED', 'Assigned'
    CANCELLED = 'CANCELLED', 'Cancelled'
    COMPLETED = 'COMPLETED', 'Completed'
    IN_PROGRESS = 'IN_PROGRESS', 'In progress'
    REQUESTED = 'REQUESTED', 'Requested'
    SCHEDULED = 'SCHEDULED', 'Scheduled'

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
        on_delete = PROTECT
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