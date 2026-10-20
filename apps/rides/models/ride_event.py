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
    
    class Meta:
        indexes = [
            models.Index(
                fields = ['ride', '-created_at'],
                name = 'ride_created_at_idx'
            )
        ]