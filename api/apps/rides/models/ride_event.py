from django.conf import settings
from django.db import models
from .ride import Ride

class RideEvent(models.Model):
    ride = models.ForeignKey(
        Ride,
        related_name = 'events',
        on_delete = models.PROTECT
    )
    description = models.CharField(
        max_length = 255
    )
    created_at = models.DateTimeField(auto_now_add = True)
    occurred_at = models.DateTimeField(null=True, blank=True, db_index=True)

    @property
    def effective_time(self):
        return self.occurred_at or self.created_at
    
    class Meta:
        indexes = [
            models.Index(
                fields = ['ride', '-created_at'],
                name = 'ride_created_at_idx'
            ),
            models.Index(
                fields = ['ride', 'occurred_at'],
                name = 'ride_occurred_at_idx'
            )
        ]


class RideEventCorrection(models.Model):
    event = models.ForeignKey(
        RideEvent,
        related_name='corrections',
        on_delete=models.CASCADE
    )
    corrected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='event_corrections',
        on_delete=models.PROTECT
    )
    previous_occurred_at = models.DateTimeField()
    new_occurred_at = models.DateTimeField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
