from django.db import models
from django.conf import settings

# Create your models here.
class Statuses(models.TextChoices):
    ASSIGNED = 'ASSIGNED', 'Assigned'
    CANCELLED = 'CANCELLED', 'Cancelled'
    COMPLETED = 'COMPLETED', 'Completed'
    IN_PROGRESS = 'IN_PROGRESS', 'In progress'
    REQUESTED = 'REQUESTED', 'Requested'
    SCHEDULED = 'SCHEDULED', 'Scheduled'

class Ride(models.Model):
    status = models.CharField(
        max_length = 15,
        choices = Statuses.choices,
        default = Statuses.REQUESTED,
        db_default = Statuses.REQUESTED
    )
    id_rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'rider_rides',
        on_delete = models.PROTECT
    )
    id_driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'drive_rides',
        on_delete = models.PROTECT
    )
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check = models.Q(status__in = Statuses.values),
                name = 'status_constraint'
            )
        ]